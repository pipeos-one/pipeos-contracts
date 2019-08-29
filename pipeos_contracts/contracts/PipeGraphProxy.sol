pragma solidity ^0.5.4;
pragma experimental ABIEncoderV2;


contract PipeGraphProxy {

    uint256 public count = 1;
    mapping(uint256 => ProgEx) public testingDefaultsProgEx;

    struct Step {
        address contractAddress;
        bytes4 functionSig;
        uint8[] inputIndexes;
        bool[] outputIsStatic;
    }

    struct ProgEx {
        // packed encoded inputs
        bytes inputs;
        bool[] inputIsStatic;
        // starts are of length inputIsStatic.length + 1
        uint8[] starts;
        uint8[] outputIndexes;
        Step[] steps;
    }

    function addTestProgEx(ProgEx memory prog) public {
        ProgEx storage progex = testingDefaultsProgEx[count];
        progex.inputs = prog.inputs;
        progex.inputIsStatic = prog.inputIsStatic;
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
            length += script.steps[i].outputIsStatic.length;
        }

        uint8[] memory starts = new uint8[](length);
        bool[] memory inputIsStatic = new bool[](length - 1);

        uint8 j;
        for (j = 0; j < script.starts.length - 1; j ++) {
            starts[j] = script.starts[j];
            inputIsStatic[j] = script.inputIsStatic[j];
        }
        starts[j] = script.starts[j];

        for (uint8 i = 0; i < script.steps.length; i ++) {
            // Build inputs needed to make the transaction / call in this step
            bytes memory inputs = buildInput(script.inputs, script.steps[i].inputIndexes, inputIsStatic, starts);

            (bool success, bytes memory output) = script.steps[i].contractAddress.staticcall(
                abi.encodePacked(script.steps[i].functionSig, inputs)
            );
            require(success == true, 'Staticcall failed');

            // Get output for step and insert it in the inputs
            uint8 index = 0;
            for (uint8 out = 0; out < script.steps[i].outputIsStatic.length; out ++) {
                if (script.steps[i].outputIsStatic[out] == true) {
                    bytes32 addition = getStaticArgument(output, index);
                    script.inputs = abi.encodePacked(script.inputs, addition);

                    starts[startsLen] = starts[startsLen - 1] + 32;
                    inputIsStatic[startsLen - 1] = true;
                    index += 32;
                    startsLen += 1;
                } else {

                }
            }
        }

        // Return all the outputs referenced in outputIndexes
        for (uint8 i = 0; i < script.outputIndexes.length; i ++) {
            if (inputIsStatic[script.outputIndexes[i]] == true) {
                result = abi.encodePacked(result, getStaticArgument(script.inputs, starts[script.outputIndexes[i]]));
            } else {
                result = abi.encodePacked(
                    result,
                    getDynamicArgument(script.inputs, starts[script.outputIndexes[i]], starts[script.outputIndexes[i] + 1])
                );
            }
        }
        return result;
    }

    function getStaticArgument(bytes memory inputs, uint8 startIndex) pure public returns(bytes32 result) {
        assembly {
            let freemem_pointer := mload(0x40)
            result := mload(add(inputs, add(startIndex, 32)))
        }
    }

    function getDynamicArgument(bytes memory inputs, uint8 startIndex, uint8 endIndex) pure public returns(bytes memory result) {

    }

    function buildInput(bytes memory inputs, uint8[] memory inputIndexes, bool[] memory inputIsStatic, uint8[] memory starts) pure public returns(bytes memory result) {
        bytes memory heads;
        bytes memory tails;

        for (uint8 i = 0; i < inputIndexes.length; i++) {
            if (inputIsStatic[inputIndexes[i]] == true) {
                heads = abi.encodePacked(heads, getStaticArgument(inputs, starts[inputIndexes[i]]));
            } else {
                heads = abi.encodePacked(heads, (inputIndexes.length - i) * 32);
                tails = abi.encodePacked(tails, getDynamicArgument(inputs, starts[inputIndexes[i]], starts[inputIndexes[i + 1]]));
            }
        }
        return abi.encodePacked(heads, tails);
    }

    function getTestingDefault(uint256 index) view public returns(ProgEx memory prog) {
        return testingDefaultsProgEx[index];
    }
}
