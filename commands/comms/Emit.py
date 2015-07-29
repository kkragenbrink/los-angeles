from evennia.commands.default.muxcommand import MuxCommand

class CmdEmit(MuxCommand):
    """
    emits messages to the room you are in.

    Usage:
      @emit <message>
    """
    key = "@emit"
    aliases = ['|']
    locks = "cmd:all()"

    def func(self):
        "Run the @emit command"

        caller = self.caller

        if not self.args:
            caller.msg("@emit what?")
            return

        emit = self.args

        # calling the emit hook on the location
        emit = caller.location.at_emit(caller, emit)

        # Build the string to emit
        emit_string = '%s{n' % (emit)

        # todo: Fix msg_contents speed.
        #   We send the message to the caller directly because msg_contents is slow
        #   as sin.  This is not acceptable behaviour, but since players will never
        #   realise that their stuff is being emitted much slower than they expect,
        #   it will work for now.
        caller.msg(emit_string)
        caller.location.msg_contents(emit_string, exclude=caller, from_obj=caller)
