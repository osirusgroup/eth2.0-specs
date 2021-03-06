from typing import Any
from eth2spec.utils.ssz.ssz_impl import hash_tree_root
from eth2spec.utils.ssz.ssz_typing import (
    SSZType, SSZValue, uint, Container, ByteList, List, boolean,
    Vector, ByteVector
)


def decode(data: Any, typ: SSZType) -> SSZValue:
    if issubclass(typ, (uint, boolean)):
        return typ(data)
    elif issubclass(typ, (List, Vector)):
        return typ(decode(element, typ.elem_type) for element in data)
    elif issubclass(typ, (ByteList, ByteVector)):
        return typ(bytes.fromhex(data[2:]))
    elif issubclass(typ, Container):
        temp = {}
        for field_name, field_type in typ.get_fields().items():
            temp[field_name] = decode(data[field_name], field_type)
            if field_name + "_hash_tree_root" in data:
                assert (data[field_name + "_hash_tree_root"][2:] ==
                        hash_tree_root(temp[field_name]).hex())
        ret = typ(**temp)
        if "hash_tree_root" in data:
            assert (data["hash_tree_root"][2:] ==
                    hash_tree_root(ret).hex())
        return ret
    else:
        raise Exception(f"Type not recognized: data={data}, typ={typ}")
