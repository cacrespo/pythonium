import attr

from .core import Position, StellarThing
from .orders.request import ShipOrderRequest
from .ship_type import ShipType
from .vectors import Transfer


@attr.s(auto_attribs=True, repr=False)
class Ship(StellarThing):
    """
    A ship that belongs to a race.

    It can be moved from one point to another, it can be used to move any resource, \
    and in some cases can be used to attack planets or ships.
    """

    thing_type = "ship"

    type: ShipType = attr.ib(
        validator=[attr.validators.instance_of((ShipType, type(None)))],
        kw_only=True,
    )
    """
    Name of the :class:`ShipType`
    """

    max_cargo: int = attr.ib(converter=int, kw_only=True)
    """
    Indicates how much pythonium and clans (together) can carry the ship.
    See :attr:`ShipType.max_cargo`
    """

    max_mc: int = attr.ib(converter=int, kw_only=True)
    """
    Indicates how much megacredits can carry the ship.
    See :attr:`ShipType.max_mc`
    """

    attack: int = attr.ib(converter=int, kw_only=True)
    """
    Indicates how much attack the ship has.
    See :attr:`ShipType.attack`
    """

    speed: int = attr.ib(converter=int, kw_only=True)
    """
    Ship's speed in ly per turn
    """

    # State in turn
    megacredits: int = attr.ib(converter=int, default=0)
    """
    Amount of megacredits on the ship
    """

    pythonium: int = attr.ib(converter=int, default=0)
    """
    Amount of pythonium on the ship
    """

    clans: int = attr.ib(converter=int, default=0)
    """
    Amount of clans on the ship
    """

    # User controls
    target: Position = attr.ib(converter=Position, default=None)
    """
    **Attribute that can be modified by the player**

    Indicates where the ship is going, or ``None`` if it is stoped.
    """

    transfer: Transfer = attr.ib(default=Transfer())
    """
    **Attribute that can be modified by the player**

    Indicates what resources will be transferred by the ship in the current turn.

    If no transfer is made this is an empty transfer.

    See :class:`Transfer` bool conversion.
    """

    def __str__(self):
        return f"Ship(id={self.id}, position={self.position}, player={self.player})"

    def __repr__(self):
        return self.__str__()

    def move(self, position: Position) -> None:
        self.target = position

    def get_orders(self):
        """
        Compute orders based on player control attributes: ``transfer`` and ``target``
        """
        orders = []
        if self.transfer:
            orders.append(
                ShipOrderRequest(
                    name="ship_transfer",
                    player=self.player,
                    id=self.id,
                    kwargs={"transfer": self.transfer},
                )
            )

        if self.target is not None:
            orders.append(
                ShipOrderRequest(
                    name="ship_move",
                    player=self.player,
                    id=self.id,
                    kwargs={"target": self.target},
                )
            )

        return orders

    @classmethod
    def deserialize(cls, data):
        transfer_data = data.pop("transfer")
        transfer = Transfer(**transfer_data)
        ship_type_data = data.pop("type")
        ship_type_cost = Transfer(**ship_type_data.pop("cost"))
        ship_type = ShipType(**ship_type_data, cost=ship_type_cost)
        return cls(**data, transfer=transfer, type=ship_type)
