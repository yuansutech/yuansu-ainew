-module(chat_server).
-behaviour(gen_server).
-export([start_link/0, join/2, send_message/3, leave/2, get_members/1]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2]).
-record(state, {rooms = #{}, members = #{}}).
start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).
join(Room, User) ->
    gen_server:call(?MODULE, {join, Room, User}).
send_message(Room, User, Message) ->
    gen_server:cast(?MODULE, {message, Room, User, Message}).
leave(Room, User) ->
    gen_server:call(?MODULE, {leave, Room, User}).
get_members(Room) ->
    gen_server:call(?MODULE, {members, Room}).
init([]) ->
    {ok, #state{}}.
handle_call({join, Room, User}, _From, State = #state{rooms = Rooms, members = Members}) ->
    RoomMembers = maps:get(Room, Members, []),
    NewMembers = Members#{Room => [User | RoomMembers]},
    NewRooms = Rooms#{Room => true},
    {reply, ok, State#state{rooms = NewRooms, members = NewMembers}};
handle_call({leave, Room, User}, _From, State = #state{members = Members}) ->
    RoomMembers = maps:get(Room, Members, []),
    NewMembers = Members#{Room => lists:delete(User, RoomMembers)},
    {reply, ok, State#state{members = NewMembers}};
handle_call({members, Room}, _From, State = #state{members = Members}) ->
    RoomMembers = maps:get(Room, Members, []),
    {reply, RoomMembers, State};
handle_call(_Request, _From, State) ->
    {reply, {error, unknown_request}, State}.
handle_cast({message, Room, User, Message}, State = #state{members = Members}) ->
    RoomMembers = maps:get(Room, Members, []),
    lists:foreach(
        fun(Member) ->
            io:format("~s received from ~s: ~s~n", [Member, User, Message])
        end,
        RoomMembers
    ),
    {noreply, State};
handle_cast(_Msg, State) ->
    {noreply, State}.
handle_info(_Info, State) ->
    {noreply, State}.
demo() ->
    {ok, _Pid} = start_link(),
    ok = join(<<"general">>, <<"alice">>),
    ok = join(<<"general">>, <<"bob">>),
    send_message(<<"general">>, <<"alice">>, <<"hello everyone">>),
    Members = get_members(<<"general">>),
    io:format("Members: ~p~n", [Members]),
    Missing = get_members(<<"nonexistent">>),
    io:format("First member: ~s~n", [hd(Missing)]),
    ok.
