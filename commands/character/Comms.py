from evennia.commands.default.muxcommand import MuxCommand
from evennia import logger
import time

class CmdEmit(MuxCommand):
    """
    emits messages to the room you are in.

    Usage:
      @emit <message>

    This will output a message with no visible prefix or postfix.

    If you wish to know who is emitting to you, set the nospoof flag on yourself.
    """
    key = "@emit"
    aliases = ['emit', '|']
    locks = "cmd:all()"
    help_category = "Roleplay"

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
        #   as sin.  This is not acceptable behaviour, but since characters will never
        #   realise that their stuff is being emitted much slower than they expect,
        #   it will work for now.
        caller.msg(emit_string, from_obj=caller)
        caller.location.msg_contents(emit_string, exclude=caller, from_obj=caller)


class CmdPage(MuxCommand):
    """
    send a private message to another character

    Usage:
      page [<character>,<character>,... =] <message>

    Send a message to target user (if online). If no
    argument is given, you will get a list of your latest messages.
    """

    key = "page"
    aliases = ['tell']
    locks = "cmd:not pperm(page_banned)"
    help_category = "Comms"

    def func(self):
        "Implement function using the Msg methods"
        # todo: Add admin "Player" paging

        caller = self.caller

        if not self.args:
            if len(caller.db.last_paged) > 0:
                names = []
                for target in caller.db.last_paged:
                    names.append(target.name)
                self.msg("You last paged {c%s{n." % ", ".join(names))
            else:
                self.msg("You haven't paged anyone, yet.")
            return

        if not self.rhs:
            if len(caller.db.last_paged) > 0:
                targets = caller.db.last_paged
            else:
                self.msg("You haven't paged anyone, yet.")
                return
        else:
            targets = []
            problems = []
            for target in set(self.lhslist):
                character = caller.search(target, global_search=True)
                if character is None:
                    problems.append("%s is not a valid character." % target)
                    continue
                if not character.access(caller, 'msg'):
                    problems.append("You are not allowed to page %s." % character.name)
                    continue
                if not hasattr(character, 'sessions') and not character.sessions:
                    problems.append("%s is offline." % character.name)
                    continue
                targets.append(character)
            if problems and targets:
                self.msg("\n".join(problems))

        if not targets:
            self.msg("No one found to page.")
            return

        msg = self.rhs

        multipage = None
        if len(targets) > 1:
            names = []
            for target in targets:
                names.append("{c%s{n" % target.name)
            multipage = ", ".join(names)

        # if message begins with a :, we assume it is a 'page-pose'
        if msg.startswith(":"):
            oheader = "From afar,"
            iheader = "Long distance to"
            if multipage is not None:
                oheader = "%s to (%s)" % (oheader, multipage)
                iheader = "%s (%s)" % (iheader, multipage)
            else:
                iheader = "%s {c%s{n" % (iheader, targets[0].name)
            message = ": {c%s{n(%s) %s" % (caller.name, caller.dbref, msg.strip(':').strip())
        elif msg.startswith(";"):
            oheader = "From afar,"
            iheader = "Long distance to"
            if multipage is not None:
                oheader = "%s to (%s)" % (oheader, multipage)
                iheader = "%s (%s)" % (iheader, multipage)
            else:
                iheader = "%s {c%s{n" % (iheader, targets[0].name)
            message = ": {c%s{n(%s)%s" % (caller.name, caller.dbref, msg.strip(';').strip())
        else:
            if multipage is not None:
                oheader = "To (%s), {c%s{n(%s) pages: %s" % (multipage, caller.name, caller.dbref, msg)
                iheader = "You paged (%s): %s" % (multipage, msg)
            else:
                oheader = "{c%s{n(%s) pages: %s" % (caller.name, caller.dbref, msg)
                iheader = "You paged {c%s{n with '%s'" % (targets[0].name, msg)
            message = ""

        # send the messages to their destinations

       
        logger.log_info("%s" % (caller == targets[0]))
        logger.log_info("%s\n%s" % (caller.__dict__, targets[0].__dict__))
        caller.msg("%s%s" % (iheader, message))
        for target in targets:
            target.msg("%s%s" % (oheader, message))
        # save the last paged
        caller.db.last_paged = targets
