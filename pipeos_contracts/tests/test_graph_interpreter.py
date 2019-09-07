from web3 import Web3
from eth_abi import encode_single, encode_abi, decode_abi
from pipeos_contracts.tests.utils.encoding import (
    get_function_signature,
    prepareGraphProxyInputs,
)


# !graph arrays significant values start from index 1
# due to valueIndex, that can be 0

def test_getSlot(pipe_graph_interpreter):
    product_id = 1
    wei_value = 100
    (inputs, _, _) = prepareGraphProxyInputs(
        ['uint256', 'uint256'],
        [product_id, wei_value],
    )
    prodid = pipe_graph_interpreter.functions.getSlot(inputs, 0).call()
    wei = pipe_graph_interpreter.functions.getSlot(inputs, 32).call()
    assert prodid == encode_single('uint256', product_id)
    assert wei == encode_single('uint256', wei_value)


def test_getPartialBytes(pipe_graph_interpreter):
    static_array = [1, 2, 3]
    uint = 100
    dynamic_array = [5, 6, 7]
    struct = {
        'bool': False,
        'bytes': Web3.toBytes(text='Hello'),
        'uint16': 3,
    }
    vendor = '0x1111111111111111111111111111111111111111'
    string = (
        f'Some long string that is bigger than bytes32 and goes on another slot. '
        f'Some long string that is bigger than bytes32 and goes on another slot. '
        f'Some long string that is bigger than bytes32 and goes on another slot.'
    )
    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256[3]', 'uint256', 'uint256[]', '(bool,bytes,uint16)', 'address', 'string'],
        [static_array, uint, dynamic_array, list(struct.values()), vendor, string],
    )

    get_static_array = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[1],
        starts[2],
    ).call()
    assert get_static_array == encode_single('uint256[3]', static_array)

    get_uint = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[2],
        starts[3],
    ).call()
    assert get_uint == encode_single('uint256', uint)

    get_dynamic_array = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[3],
        starts[4],
    ).call()
    assert get_dynamic_array == encode_single('uint256[]', dynamic_array)

    get_struct = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[4],
        starts[5],
    ).call()
    assert get_struct == encode_single('(bool,bytes,uint16)', list(struct.values()))

    get_vendor = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[5],
        starts[6],
    ).call()
    assert get_vendor == encode_single('address', vendor)

    get_string = pipe_graph_interpreter.functions.getPartialBytes(
        inputs,
        starts[6],
        starts[7],
    ).call()
    assert get_string == encode_single('string', string)


def test_buildAbiIO_one_slot(pipe_graph_interpreter):
    product_id = 1
    wei_value = 100
    vendor = '0x1111111111111111111111111111111111111111'
    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256', 'uint256', 'address'],
        [product_id, wei_value, vendor],
    )

    inputIndexes = [1]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    assert built_input == encode_single('uint256', product_id)

    inputIndexes = [2]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    assert built_input == encode_single('uint256', wei_value)

    inputIndexes = [3]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    assert built_input == encode_single('address', vendor)

    inputIndexes = [1, 3]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    assert built_input == (
        encode_single('uint256', product_id)
        + encode_single('address', vendor)
    )

    inputIndexes = [1, 3, 2]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    assert built_input == (
        encode_single('uint256', product_id)
        + encode_single('address', vendor)
        + encode_single('uint256', wei_value)
    )


def test_buildAbiIO_multiple_slots(pipe_graph_interpreter, pipegraph_proxy_test, get_accounts):
    uint = 5
    dynamic_array = [5, 6, 7]
    address = get_accounts(1)[0]
    t_struct = [uint, dynamic_array, address]

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256[]', 'uint256', 'address'],
        [dynamic_array, uint, address],
    )
    inputIndexes = [1, 2, 3]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    tx_data = pipegraph_proxy_test.functions.t_array(
        dynamic_array,
        uint,
        address,
    ).buildTransaction()
    assert Web3.toHex(built_input)[2:] == tx_data['data'][10:]

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['(uint256,uint256[],address)'],
        [t_struct],
    )
    inputIndexes = [1]
    built_input = pipe_graph_interpreter.functions.buildAbiIO(
        inputs,
        inputIndexes,
        inputSizeIsSlot,
        starts,
    ).call()
    tx_data = pipegraph_proxy_test.functions.t_struct(t_struct).buildTransaction()
    assert Web3.toHex(built_input)[2:] == tx_data['data'][10:]


def test_run_one_slot(
        pipe_graph_interpreter,
        vendor_reg_contract,
        vendor_prices_contract,
        market_contract,
):
    product_id = 1
    wei_value = 100
    vendor = vendor_reg_contract.functions.getVendor(product_id).call()
    quantity = vendor_prices_contract.functions.calculateQuantity(
        product_id,
        vendor,
        wei_value,
    ).call()

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256', 'uint256'],
        [product_id, wei_value],
    )
    functionSig1 = get_function_signature('getVendor', ['uint256'])
    functionSig2 = get_function_signature('calculateQuantity', ['uint256', 'address', 'uint256'])

    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': vendor_reg_contract.address,
                'functionSig': functionSig1,
                'inputIndexes': [1],
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
            {
                'contractAddress': vendor_prices_contract.address,
                'functionSig': functionSig2,
                'inputIndexes': [1, 3, 2],
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
        ],
        'outputIndexes': [4],
    }
    pipe_graph_interpreter.functions.addTestProgEx(progex).transact()
    inserted = pipe_graph_interpreter.functions.getTestingDefault(1).call()
    assert progex['inputs'] == inserted[0]
    assert progex['inputSizeIsSlot'] == inserted[1]
    assert progex['outputIndexes'] == inserted[2]
    assert progex['starts'] == inserted[3]
    assert len(progex['steps']) == len(inserted[4])
    assert progex['steps'][0]['contractAddress'] == inserted[4][0][0]
    assert progex['steps'][0]['functionSig'] == inserted[4][0][1]
    assert progex['steps'][0]['valueIndex'] == inserted[4][0][2]
    assert progex['steps'][0]['inputIndexes'] == inserted[4][0][3]
    assert progex['steps'][0]['outputSizeIsSlot'] == inserted[4][0][4]
    assert progex['steps'][1]['contractAddress'] == inserted[4][1][0]
    assert progex['steps'][1]['functionSig'] == inserted[4][1][1]
    assert progex['steps'][1]['valueIndex'] == inserted[4][1][2]
    assert progex['steps'][1]['inputIndexes'] == inserted[4][1][3]
    assert progex['steps'][1]['outputSizeIsSlot'] == inserted[4][1][4]

    answer = pipe_graph_interpreter.functions.run(progex).call()
    assert Web3.toInt(answer) == quantity

    answer = pipe_graph_interpreter.functions.runTestingDefault(1).call()
    assert Web3.toInt(answer) == quantity


def test_run_multiple_slots_simple(
        pipe_graph_interpreter,
        pipegraph_proxy_test,
        get_accounts,
):
    uint = 5

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256'],
        [uint],
    )

    function_sig_uint = get_function_signature('t_uint', ['uint256'])
    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_uint,
                'inputIndexes': [1],
                'valueIndex': 0,
                'outputSizeIsSlot': [False],
            },
        ],
        'outputIndexes': [2],
    }
    pipe_graph_interpreter.functions.addTestProgEx(progex).transact()
    inserted = pipe_graph_interpreter.functions.getTestingDefault(1).call()
    assert progex['inputs'] == inserted[0]
    assert progex['inputSizeIsSlot'] == inserted[1]
    assert progex['outputIndexes'] == inserted[2]
    assert progex['starts'] == inserted[3]
    assert len(progex['steps']) == len(inserted[4])
    assert progex['steps'][0]['contractAddress'] == inserted[4][0][0]
    assert progex['steps'][0]['functionSig'] == inserted[4][0][1]
    assert progex['steps'][0]['valueIndex'] == inserted[4][0][2]
    assert progex['steps'][0]['inputIndexes'] == inserted[4][0][3]
    assert progex['steps'][0]['outputSizeIsSlot'] == inserted[4][0][4]

    answer = pipe_graph_interpreter.functions.run(progex).call()
    uarray = pipegraph_proxy_test.functions.t_uint(uint).call()
    decoded_answer = decode_abi(['uint256[]'], answer)
    assert list(decoded_answer[0]) == uarray

    answer = pipe_graph_interpreter.functions.runTestingDefault(1).call()
    decoded_answer = decode_abi(['uint256[]'], answer)
    assert list(decoded_answer[0]) == uarray


def test_run_multiple_slots_2(
        pipe_graph_interpreter,
        pipegraph_proxy_test,
        get_accounts,
):
    uint = 5

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256'],
        [uint],
    )

    function_sig_uint = get_function_signature('t_uint', ['uint256'])
    function_sig_address = get_function_signature('t_address', [])
    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_uint,
                'inputIndexes': [1],
                'valueIndex': 0,
                'outputSizeIsSlot': [False],
            },
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_address,
                'inputIndexes': [],
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
        ],
        'outputIndexes': [2, 3],
    }

    pipe_graph_interpreter.functions.addTestProgEx(progex).transact()
    inserted = pipe_graph_interpreter.functions.getTestingDefault(1).call()
    assert progex['inputs'] == inserted[0]
    assert progex['inputSizeIsSlot'] == inserted[1]
    assert progex['outputIndexes'] == inserted[2]
    assert progex['starts'] == inserted[3]
    assert len(progex['steps']) == len(inserted[4])
    assert progex['steps'][0]['contractAddress'] == inserted[4][0][0]
    assert progex['steps'][0]['functionSig'] == inserted[4][0][1]
    assert progex['steps'][0]['valueIndex'] == inserted[4][0][2]
    assert progex['steps'][0]['inputIndexes'] == inserted[4][0][3]
    assert progex['steps'][0]['outputSizeIsSlot'] == inserted[4][0][4]
    assert progex['steps'][1]['contractAddress'] == inserted[4][1][0]
    assert progex['steps'][1]['functionSig'] == inserted[4][1][1]
    assert progex['steps'][1]['valueIndex'] == inserted[4][1][2]
    assert progex['steps'][1]['inputIndexes'] == inserted[4][1][3]
    assert progex['steps'][1]['outputSizeIsSlot'] == inserted[4][1][4]

    answer = pipe_graph_interpreter.functions.run(progex).call()
    uarray = pipegraph_proxy_test.functions.t_uint(uint).call()
    encoded_answer = encode_abi(
        ['uint256[]', 'address'],
        [uarray, pipe_graph_interpreter.address],
    )
    assert answer == encoded_answer

    decoded_answer = decode_abi(['uint256[]', 'address'], answer)
    assert list(decoded_answer[0]) == uarray
    assert decoded_answer[1] == pipe_graph_interpreter.address.lower()


def test_run_multiple_slots_multiple_outputs(
        pipe_graph_interpreter,
        pipegraph_proxy_test,
        get_accounts,
):
    uint = 5
    dynamic_array = [5, 6, 7]
    address = get_accounts(1)[0]
    t_struct = [uint, dynamic_array, address]

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['(uint256,uint256[],address)'],
        [t_struct],
    )

    function_sig_struct = get_function_signature('t_struct', ['(uint256,uint256[],address)'])

    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_struct,
                'inputIndexes': [1],
                'valueIndex': 0,
                'outputSizeIsSlot': [True, False, True],
            },
        ],
    }

    progex['outputIndexes'] = [2]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256'], answer)
    assert decoded_answer[0] == uint

    progex['outputIndexes'] = [3]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256[]'], answer)
    assert list(decoded_answer[0]) == dynamic_array

    progex['outputIndexes'] = [4]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['address'], answer)
    assert decoded_answer[0] == address.lower()

    progex['outputIndexes'] = [2, 3]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256', 'uint256[]'], answer)
    assert decoded_answer[0] == uint
    assert list(decoded_answer[1]) == dynamic_array


def test_run_multiple_slots_multiple_outputs_complex(
        pipe_graph_interpreter,
        pipegraph_proxy_test,
        get_accounts,
):
    uint = 5

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256'],
        [uint],
    )

    function_sig_uint = get_function_signature('t_uint', ['uint256'])
    function_sig_address = get_function_signature('t_address', [])
    function_sig_array = get_function_signature('t_array', ['uint256[]', 'uint256', 'address'])
    function_sig_struct = get_function_signature('t_struct', ['(uint256,uint256[],address)'])

    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_uint,
                'inputIndexes': [1],
                'valueIndex': 0,
                'outputSizeIsSlot': [False],
            },
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_address,
                'inputIndexes': [],
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_array,
                'inputIndexes': [2, 1, 3],
                'valueIndex': 0,
                'outputSizeIsSlot': [False],
            },
            {
                'contractAddress': pipegraph_proxy_test.address,
                'functionSig': function_sig_struct,
                'inputIndexes': [4],
                'valueIndex': 0,
                'outputSizeIsSlot': [True, False, True],
            },
        ],
    }

    uarray = pipegraph_proxy_test.functions.t_uint(uint).call()

    progex['outputIndexes'] = [1]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256'], answer)
    assert decoded_answer[0] == uint

    progex['outputIndexes'] = [1, 4]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256', '(uint256,uint256[],address)'], answer)
    assert decoded_answer[0] == uint
    assert decoded_answer[1][0] == uint
    assert list(decoded_answer[1][1]) == uarray
    assert decoded_answer[1][2] == pipe_graph_interpreter.address.lower()

    progex['outputIndexes'] = [5]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256'], answer)
    assert decoded_answer[0] == uint

    progex['outputIndexes'] = [6]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256[]'], answer)
    assert list(decoded_answer[0]) == uarray

    progex['outputIndexes'] = [5, 6, 7]
    answer = pipe_graph_interpreter.functions.run(progex).call()
    decoded_answer = decode_abi(['uint256', 'uint256[]', 'address'], answer)
    assert decoded_answer[0] == uint
    assert list(decoded_answer[1]) == uarray
    assert decoded_answer[2] == pipe_graph_interpreter.address.lower()


def test_run_payable(
        web3,
        get_accounts,
        pipe_graph_interpreter,
        vendor_reg_contract,
        vendor_prices_contract,
        market_contract,
):
    product_id = 1
    wei_value = 100
    buyer = get_accounts(1)[0]
    vendor = vendor_reg_contract.functions.getVendor(product_id).call()
    quantity = vendor_prices_contract.functions.calculateQuantity(
        product_id,
        vendor,
        wei_value,
    ).call()

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['address', 'address', 'uint256', 'uint256', 'uint256'],
        [vendor, buyer, product_id, quantity, wei_value],
    )
    sigBuy = get_function_signature('buy', ['address', 'address', 'uint256', 'uint256'])

    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': market_contract.address,
                'functionSig': sigBuy,
                'inputIndexes': [1, 2, 3, 4],  # vendor, buyer, product_id, quantity, wei_value
                'valueIndex': 5,
                'outputSizeIsSlot': [],
            },
        ],
        'outputIndexes': [],
    }

    prod_quantity_pre = market_contract.functions.getQuantity(vendor, product_id).call()
    txn_hash = pipe_graph_interpreter.functions.run(progex).transact({'value': wei_value})
    prod_quantity_post = market_contract.functions.getQuantity(vendor, product_id).call()

    assert prod_quantity_pre - quantity == prod_quantity_post

    txn_hash2 = market_contract.functions.buy(vendor, buyer, product_id, quantity).transact({
        'value': wei_value,
    })
    print('test_run_payable run', web3.eth.getTransactionReceipt(txn_hash)['cumulativeGasUsed'])
    print('test_run_payable buy', web3.eth.getTransactionReceipt(txn_hash2)['cumulativeGasUsed'])


def test_run_transaction_mix(
        web3,
        get_accounts,
        pipe_graph_interpreter,
        vendor_reg_contract,
        vendor_prices_contract,
        market_contract,
):
    product_id = 1
    wei_value = 100
    buyer = get_accounts(1)[0]
    vendor = vendor_reg_contract.functions.getVendor(product_id).call()
    quantity = vendor_prices_contract.functions.calculateQuantity(
        product_id,
        vendor,
        wei_value,
    ).call()

    (inputs, starts, inputSizeIsSlot) = prepareGraphProxyInputs(
        ['uint256', 'address', 'uint256'],
        [product_id, buyer, wei_value],
    )
    sigGetVendor = get_function_signature('getVendor', ['uint256'])
    sigCalculateQuantity = get_function_signature(
        'calculateQuantity',
        ['uint256', 'address', 'uint256'],
    )
    sigBuy = get_function_signature('buy', ['address', 'address', 'uint256', 'uint256'])

    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputSizeIsSlot': inputSizeIsSlot,
        'starts': starts,
        'steps': [
            {
                'contractAddress': vendor_reg_contract.address,
                'functionSig': sigGetVendor,
                'inputIndexes': [1],  # product_id
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
            {
                'contractAddress': vendor_prices_contract.address,
                'functionSig': sigCalculateQuantity,
                'inputIndexes': [1, 4, 3],  # product_id, vendor, wei_value
                'valueIndex': 0,
                'outputSizeIsSlot': [True],
            },
            {
                'contractAddress': market_contract.address,
                'functionSig': sigBuy,
                'inputIndexes': [4, 2, 1, 5],  # vendor, buyer, product_id, quantity
                'valueIndex': 3,
                'outputSizeIsSlot': [],
            },
        ],
        'outputIndexes': [],
    }

    prod_quantity_pre = market_contract.functions.getQuantity(vendor, product_id).call()
    pipe_graph_interpreter.functions.run(progex).transact({'value': wei_value})
    prod_quantity_post = market_contract.functions.getQuantity(vendor, product_id).call()

    assert prod_quantity_pre - quantity == prod_quantity_post
