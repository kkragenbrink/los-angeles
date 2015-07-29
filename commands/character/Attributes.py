from evennia.commands.default.muxcommand import MuxCommand


class CmdSetFlag(MuxCommand):
    """
    sets flags on an object

    Usage:
      @set <object>=<flag>
    """
    key = "@set"
    aliases = ["@flag"]
    locks = "cmd:all()"

    def func(self):
        "Run the @set command"

        usage = "Usage:"
        usage += "{n@set <obj>=<flag>"

        caller = self.caller

        if not self.args:
            caller.msg(usage)
            return

        if not self.rhs:
            target = caller
            flag = self.args
        else:
            target = self.lhs
            flag = self.rhs

        value = True
        if flag[:1] == '!':
            flag = flag[1:]
            value = False

        flag = flag.lower()

        target = caller.search(target, typeclass="Character")

        if not target:
            caller.msg(usage)
            return

        if flag not in caller.db.flags.keys():
            msg = "%s is not a valid flag." % flag
            caller.msg(msg)

        if caller == target or target.access(caller, 'edit'):
            target.db.flags[flag] = value
            msg = "Set" if value else "Unset"
            caller.msg(msg)
        else:
            msg = "You do not have access to modify %s" % target.name
            caller.msg(msg)
