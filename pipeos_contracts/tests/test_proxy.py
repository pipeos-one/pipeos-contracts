from pipeos_contracts.tests.utils.encoding import encode_with_selector, to_bytes


def test_proxy(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    assert piped_test_contract.functions.pipe_proxy().call() == pipe_proxy_contract.address
    assert piped_test_contract.functions.test_contract().call() == test_functions_contract.address


def test_view_memory_uint256(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = 5
    assert test_functions_contract.functions.m_uint256(io).call() == io
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('m_uint256', ['uint256'], [io]),
        0,
    ).call() == to_bytes(io)
    assert piped_test_contract.functions.m_uint256(io).call() == io


def test_view_storage_uint256(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = test_functions_contract.functions.svar().call()
    assert test_functions_contract.functions.s_uint256().call() == io
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('s_uint256'),
        0,
    ).call() == to_bytes(io)
    assert piped_test_contract.functions.s_uint256().call() == io


def test_view_memory_uint8(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = 5
    assert test_functions_contract.functions.m_uint8(io).call() == io
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('m_uint8', ['uint8'], [io]),
        0,
    ).call() == to_bytes(io)
    assert piped_test_contract.functions.m_uint8(io).call() == io


def test_view_memory_uint8_uint8(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = [1, 2]
    assert test_functions_contract.functions.m_uint8_uint8(*io).call() == io
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('m_uint8_uint8', ['uint8', 'uint8'], [*io]),
        0,
    ).call() == b''.join(to_bytes(n) for n in io)
    assert piped_test_contract.functions.m_uint8_uint8(*io).call() == io


def test_view_memory_address(
        get_accounts,
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = get_accounts(1)[0]
    assert test_functions_contract.functions.m_addr(io).call() == io
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('m_addr', ['address'], [io]),
        0,
    ).call() == to_bytes(hexstr=io)
    assert piped_test_contract.functions.m_addr(io).call() == io


def test_view_storage_address(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    out = test_functions_contract.functions.s_addr().call()
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('s_addr', [], []),
        0,
    ).call() == to_bytes(hexstr=out)
    assert piped_test_contract.functions.s_addr().call() == out


def test_view_mix_tuple_address_address(
        get_accounts,
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = get_accounts(1)[0]
    out = test_functions_contract.functions.addr_addr(io).call()
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('addr_addr', ['address'], [io]),
        0,
    ).call() == to_bytes(hexstr=out[0]) + to_bytes(hexstr=out[1])
    assert piped_test_contract.functions.addr_addr(io).call() == out


def test_view_mix_tuple_address_uint_uint(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = 5
    out = test_functions_contract.functions.addr_uint_uint(io).call()
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('addr_uint_uint', ['uint256'], [io]),
        0,
    ).call() == (
        to_bytes(hexstr=out[0])
        + to_bytes(out[1])
        + to_bytes(out[2]),
    )
    assert piped_test_contract.functions.addr_uint_uint(io).call() == out


def test_view_mix_tuple_address_uint_bytes32(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = b'\x01' * 0
    out = test_functions_contract.functions.addr_uint_bytes32(io).call()
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('addr_uint_bytes32', ['bytes32'], [io]),
        0,
    ).call() == (
        to_bytes(hexstr=out[0])
        + to_bytes(out[1])
        + out[2],
    )
    assert piped_test_contract.functions.addr_uint_bytes32(io).call() == out


def test_memory_uint256_array_static(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = [1, 2, 3, 4]
    out = test_functions_contract.functions.m_uint256_arr_static(io).call()
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('m_uint256_arr_static', ['uint256[4]'], [io]),
        0,
    ).call() == b''.join(to_bytes(n) for n in out)
    assert piped_test_contract.functions.m_uint256_arr_static(io).call() == out


def test_storage_uint256_array_dynamic(
        pipe_proxy_contract,
        piped_test_contract,
        test_functions_contract,
):
    io = 8
    out = test_functions_contract.functions.get_arr().call()
    out.append(io)
    out_bytes = b''.join(to_bytes(n) for n in out)
    pipe_proxy_contract.functions.proxy(
        test_functions_contract.address,
        encode_with_selector('s_uint256_arr_dynamic', ['uint256'], [io]),
        0,
    ).call() == out_bytes
    # TODO: fix
    # assert piped_test_contract.functions.s_uint256_arr_dynamic(io).call() == out
