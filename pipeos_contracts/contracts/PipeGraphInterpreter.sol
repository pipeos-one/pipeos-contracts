pragma solidity ^0.5.4;
pragma experimental ABIEncoderV2;


contract PipeGraphInterpreter {

    uint256 public count = 1;
    mapping(uint256 => ProgEx) public testingDefaultsProgEx;

    struct Step {
        address contractAddress;
        bytes4 functionSig;
        uint8[] inputIndexes;
        bool[] outputSizeIsSlot;
    }

    struct ProgEx {
        // packed encoded inputs
        bytes inputs;
        bool[] inputSizeIsSlot;
        uint8[] outputIndexes;
        // starts are of length inputSizeIsSlot.length + 1
        uint16[] starts;
        Step[] steps;
    }

    function addTestProgEx(ProgEx memory prog) public {
        ProgEx storage progex = testingDefaultsProgEx[count];
        progex.inputs = prog.inputs;
        progex.inputSizeIsSlot = prog.inputSizeIsSlot;
        progex.starts = prog.starts;
        progex.outputIndexes = prog.outputIndexes;
        for (uint8 i = 0; i < prog.steps.length; i++) {
            progex.steps.push(prog.steps[i]);
        }
        count ++;
    }

    function runTestingDefault(uint256 index) public returns(bytes memory) {
        return run(testingDefaultsProgEx[index]);
    }

    function run(ProgEx memory script) public returns(bytes memory result) {
        uint256 startsLen = script.starts.length;
        uint256 length = startsLen;

        for (uint8 i = 0; i < script.steps.length; i ++) {
            length += script.steps[i].outputSizeIsSlot.length;
        }

        uint16[] memory starts = new uint16[](length);
        bool[] memory inputSizeIsSlot = new bool[](length - 1);

        uint16 j;
        for (j = 0; j < script.starts.length - 1; j ++) {
            starts[j] = script.starts[j];
            inputSizeIsSlot[j] = script.inputSizeIsSlot[j];
        }
        starts[j] = script.starts[j];

        for (uint8 i = 0; i < script.steps.length; i ++) {
            // Build inputs needed to make the transaction / call in this step
            bytes memory inputs = buildAbiIO(script.inputs, script.steps[i].inputIndexes, inputSizeIsSlot, starts);

            (bool success, bytes memory output) = script.steps[i].contractAddress.staticcall(
                abi.encodePacked(script.steps[i].functionSig, inputs)
            );
            require(success == true, 'Staticcall failed');

            // Get output for step and insert it in the inputs
            for (uint8 out = 0; out < script.steps[i].outputSizeIsSlot.length; out ++) {
                if (script.steps[i].outputSizeIsSlot[out] == true) {
                    bytes32 addition = getSlot(output, out * 32);
                    script.inputs = abi.encodePacked(script.inputs, addition);

                    starts[startsLen] = starts[startsLen - 1] + 32;
                    inputSizeIsSlot[startsLen - 1] = true;
                    startsLen += 1;
                } else {
                    bytes memory addition = getMultiSlotIO(output, script.steps[i].outputSizeIsSlot, out);
                    script.inputs = abi.encodePacked(script.inputs, addition);

                    starts[startsLen] = starts[startsLen - 1] + uint16(addition.length);
                    inputSizeIsSlot[startsLen - 1] = false;
                    startsLen += 1;
                }
            }
        }
        return buildAbiIO(script.inputs, script.outputIndexes, inputSizeIsSlot, starts);
    }

    function getSlot(bytes memory inputs, uint16 startIndex) pure public returns(bytes32 result) {
        assembly {
            let freemem_pointer := mload(0x40)
            result := mload(add(inputs, add(startIndex, 32)))
        }
    }

    function getNextDynamicIndex(bytes memory output, bool[] memory outputSizeIsSlot, uint8 out)
        pure public returns(uint16 index)
    {
        for (uint16 i = out; i < outputSizeIsSlot.length; i ++) {
            if (outputSizeIsSlot[i] == false) {
                uint16 offset;
                uint16 index = (i + 1) * 32;
                assembly {
                    let freemem_pointer := mload(0x40)
                    offset := mload(add(output, index))
                }
                return offset;
            }
        }
        return uint16(output.length);
    }

    function getMultiSlotIO(bytes memory output, bool[] memory outputSizeIsSlot, uint8 out) pure public returns(bytes memory addition) {
        uint16 startIndex = getNextDynamicIndex(output, outputSizeIsSlot, out);
        uint16 endIndex = getNextDynamicIndex(output, outputSizeIsSlot, out + 1);

        return getPartialBytes(output, startIndex, endIndex);
    }

    // endIndex is not included
    function getPartialBytes(bytes memory inputs, uint16 startIndex, uint16 endIndex) pure public returns(bytes memory result) {
        require(inputs.length >= endIndex);
        require(endIndex >= startIndex);

        uint16 _length = endIndex - startIndex;
        if (_length == 0) {
            return result;
        }

        assembly {
            // free memory pointer
            result := mload(0x40)

            // The first word of the slice result is potentially a partial
            // word read from the original array. To read it, we calculate
            // the length of that partial word and start copying that many
            // bytes into the array. The first word we copy will start with
            // data we don't care about, but the last `lengthmod` bytes will
            // land at the beginning of the contents of the new array. When
            // we're done copying, we overwrite the full first word with
            // the actual length of the slice.
            let lengthmod := and(_length, 31)

            // The multiplication in the next line is necessary
            // because when slicing multiples of 32 bytes (lengthmod == 0)
            // the following copy loop was copying the origin's length
            // and then ending prematurely not copying everything it should.
            let mc := add(add(result, lengthmod), mul(0x20, iszero(lengthmod)))
            let end := add(mc, _length)

            for {
                // The multiplication in the next line has the same exact purpose
                // as the one above.
                let cc := add(add(add(inputs, lengthmod), mul(0x20, iszero(lengthmod))), startIndex)
            } lt(mc, end) {
                mc := add(mc, 0x20)
                cc := add(cc, 0x20)
            } {
                mstore(mc, mload(cc))
            }

            mstore(result, _length)

            //update free-memory pointer
            //allocating the array padded to 32 bytes like the compiler does now
            mstore(0x40, and(add(mc, 31), not(31)))
        }
    }

    function buildAbiIO(bytes memory inputs, uint8[] memory inputIndexes, bool[] memory inputSizeIsSlot, uint16[] memory starts) pure public returns(bytes memory result) {
        bytes memory heads;
        bytes memory tails;

        for (uint8 i = 0; i < inputIndexes.length; i++) {
            if (inputSizeIsSlot[inputIndexes[i]] == true) {
                heads = abi.encodePacked(heads, getSlot(inputs, starts[inputIndexes[i]]));
            } else {
                heads = abi.encodePacked(heads, uint256(inputIndexes.length * 32 + tails.length));
                tails = abi.encodePacked(tails, getPartialBytes(
                    inputs,
                    starts[inputIndexes[i]],
                    starts[inputIndexes[i] + 1]
                ));
            }
        }
        return abi.encodePacked(heads, tails);
    }

    function getTestingDefault(uint256 index) view public returns(ProgEx memory prog) {
        return testingDefaultsProgEx[index];
    }
}
