from zimp.domain.common.contract_items import ItemsContract
from zimp.domain.items.inventory import Inventory
from zimp.support.items.fake_items import FakeItemsGateway


def test_real_and_fake_satisfy_items_contract() -> None:
    assert isinstance(Inventory(), ItemsContract)
    assert isinstance(FakeItemsGateway(), ItemsContract)
