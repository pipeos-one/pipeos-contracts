from web3 import Web3
from eth_abi import encode_single
from eth_abi.packed import encode_single_packed, encode_abi_packed
from pipeos_contracts.tests.utils.encoding import (
    get_function_signature,
    prepareGraphProxyInputs,
)


def test_getStaticArgument(pipe_graph_proxy_contract):
    product_id = 1
    wei_value = 100
    inputs = encode_abi_packed(['uint256', 'uint256'], [product_id, wei_value])
    prodid = pipe_graph_proxy_contract.functions.getStaticArgument(inputs, 0).call()
    wei = pipe_graph_proxy_contract.functions.getStaticArgument(inputs, 32).call()
    assert prodid == encode_single_packed('uint256', product_id)
    assert wei == encode_single_packed('uint256', wei_value)


def test_getDynamicArgument(pipe_graph_proxy_contract):
    # TODO
    print('Not implemented')


def test_buildInput_static(pipe_graph_proxy_contract):
    # TODO
    product_id = 1
    wei_value = 100
    vendor = '0x1111111111111111111111111111111111111111'
    (inputs, starts, inputIsStatic) = prepareGraphProxyInputs(
        ['uint256', 'uint256', 'address'],
        [product_id, wei_value, vendor],
    )

    inputIndexes = [0]
    built_input = pipe_graph_proxy_contract.functions.buildInput(
        inputs,
        inputIndexes,
        inputIsStatic,
        starts,
    ).call()
    assert built_input == encode_single('uint256', product_id)

    inputIndexes = [1]
    built_input = pipe_graph_proxy_contract.functions.buildInput(
        inputs,
        inputIndexes,
        inputIsStatic,
        starts,
    ).call()
    assert built_input == encode_single('uint256', wei_value)

    inputIndexes = [2]
    built_input = pipe_graph_proxy_contract.functions.buildInput(
        inputs,
        inputIndexes,
        inputIsStatic,
        starts,
    ).call()
    assert built_input == encode_single('address', vendor)

    inputIndexes = [0, 2]
    built_input = pipe_graph_proxy_contract.functions.buildInput(
        inputs,
        inputIndexes,
        inputIsStatic,
        starts,
    ).call()
    assert built_input == (
        encode_single('uint256', product_id)
        + encode_single('address', vendor)
    )

    inputIndexes = [0, 2, 1]
    built_input = pipe_graph_proxy_contract.functions.buildInput(
        inputs,
        inputIndexes,
        inputIsStatic,
        starts,
    ).call()
    assert built_input == (
        encode_single('uint256', product_id)
        + encode_single('address', vendor)
        + encode_single('uint256', wei_value)
    )


def test_buildInput_dynamic(pipe_graph_proxy_contract):
    # TODO
    print('Not implemented')


def test_run(
        pipe_graph_proxy_contract,
        vendor_reg_contract,
        vendor_prices_contract,
        market_contract,
):
    product_id = 1
    wei_value = 100
    vendor = vendor_reg_contract.functions.getVendor(product_id).call()
    # total_quantity = market_contract.functions.getQuantity(vendor, product_id).call()
    quantity = vendor_prices_contract.functions.calculateQuantity(
        product_id,
        vendor,
        wei_value,
    ).call()

    # buildTTTT = vendor_prices_contract.functions.calculateQuantity(
    #     product_id, vendor, wei_value
    # ).buildTransaction()
    # print('buildTTTT', buildTTTT)
    # print(total_quantity, quantity)

    (inputs, starts, inputIsStatic) = prepareGraphProxyInputs(
        ['uint256', 'uint256'],
        [product_id, wei_value],
    )
    functionSig1 = get_function_signature('getVendor', ['uint256'])
    functionSig2 = get_function_signature('calculateQuantity', ['uint256', 'address', 'uint256'])

    # Prepare ProgEx input
    progex = {
        'inputs': inputs,
        'inputIsStatic': inputIsStatic,
        'starts': starts,
        'steps': [
            {
                'contractAddress': vendor_reg_contract.address,
                'functionSig': functionSig1,
                'inputIndexes': [0],
                'outputIsStatic': [True],
            },
            {
                # 'contractAddress': market_contract.address,
                # 'functionSig': get_function_signature('getQuantity', ['address', 'uint256']),
                'contractAddress': vendor_prices_contract.address,
                'functionSig': functionSig2,
                'inputIndexes': [0, 2, 1],
                'outputIsStatic': [True],
            },
        ],
        'outputIndexes': [3],
    }
    pipe_graph_proxy_contract.functions.addTestProgEx(progex).transact()
    inserted = pipe_graph_proxy_contract.functions.getTestingDefault(1).call()
    assert progex['inputs'] == inserted[0]
    assert progex['inputIsStatic'] == inserted[1]
    assert progex['starts'] == inserted[2]
    assert progex['outputIndexes'] == inserted[3]
    assert len(progex['steps']) == len(inserted[4])
    assert progex['steps'][0]['contractAddress'] == inserted[4][0][0]
    assert progex['steps'][0]['functionSig'] == inserted[4][0][1]
    assert progex['steps'][0]['inputIndexes'] == inserted[4][0][2]
    assert progex['steps'][0]['outputIsStatic'] == inserted[4][0][3]
    assert progex['steps'][1]['contractAddress'] == inserted[4][1][0]
    assert progex['steps'][1]['functionSig'] == inserted[4][1][1]
    assert progex['steps'][1]['inputIndexes'] == inserted[4][1][2]
    assert progex['steps'][0]['outputIsStatic'] == inserted[4][1][3]

    answer = pipe_graph_proxy_contract.functions.run(progex).call()
    assert Web3.toInt(answer) == quantity

    answer = pipe_graph_proxy_contract.functions.runTestingDefault(1).call()
    assert Web3.toInt(answer) == quantity
