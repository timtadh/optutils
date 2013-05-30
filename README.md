optutils
========

Small, composable utilities for writing great command line tools. Writing
a great command line tool takes art as well as science. Unlike libraries and
frameworks, commandline tools are used interactively by the programmer.
Therefore, their input interface must be forgiving yet consistent, their output
must be computer parsable yet human readable, and their error messages must be
terse yet informative.

#### `Optutils` philosophy:

1. Fail fast -- give the user immediate feedback on what they did wrong.
2. Testable Errors -- provide consistent unique exit status codes to ensure
   future testability.
3. Informative Errors -- point the way to the narrow path.
4. Separate Feedback and Output -- feedback for humans should go on the standard
   error, output for programs to the standard out.
5. Prioritize Clarity over Code -- the user experience should be paramount, not
   the programmer's experience. These utilities are not always designed to make
   the text of the program shorter, they are designed to make the user
   experience *better*.
6. Every Child is Special -- every utility is just a little different and one
   size fits all solutions tend to fit no one. Utilities should therefore be
   specialized *yet* re-usable.

# A Minimal Optutils Program with a Subcommand

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    #Author: Tim Henderson
    #Email: tim.tadh@gmail.com, tadh@case.edu
    #For licensing see the LICENSE file in the top level directory.


    import os, sys, json

    import optutils
    from optutils import output, log, error_codes, add_code


    __version__ = 'git master'

    add_code('version')

    def version():
        '''Print version and exits'''
        log('version :', __version__)
        sys.exit(error_codes['version'])


    @optutils.main(
        'usage: example <command>',
        '''
        Example:

            $ example command what

        Options
            -h, help                      print this message
            -v, version                   print the version
        ''',
        'hv',
        ['help', 'version'],
    )
    def main(argv, util, parser):
        """
        The main entry point to the program
        """

        @util.command(
            'usage: command [args]',
            '''
            Example:

            Options
                -h, help                      print this message
            ''',
            'h',
            ['help',],
        )
        def command(argv, util, parser, setting):

            opts, args = parser(argv)
            for opt, arg in opts:
                if opt in ('-h', '--help',):
                    util.usage()

            print ' '.join(args)
            print 'running with', setting


        opts, args = parser(argv)
        for opt, arg in opts:
            if opt in ('-h', '--help',):
                util.usage()
            elif opt in ('-v', '--version',):
                version()

        setting = 'wizards'

        util.run_command(args, setting)

    if __name__ == '__main__':
        sys.exit(main(sys.argv[1:]))


