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

