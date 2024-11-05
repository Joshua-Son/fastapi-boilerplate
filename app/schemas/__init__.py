from app.schemas.message import Message, ResponseBase, SuccessResponse, ErrorResponse 
from app.schemas.participation import ParticipationBase, ParticipationCreate, ParticipationResponse, ParticipationDeleteAPI
from app.schemas.arena import ArenaBase, ArenaCreate,ArenaUpdate, ArenaResponse, ArenaMultiCreateAPI, SignalAPI
from app.schemas.gamestream import GameStreamBase, GameStreamCreate, GameStreamUpdate, GameStreamResponse, GameStreamReserve, GameStreamReleaseQuit, GameStartModel, VMStatus