# NOTE: This is the documentation for an old version of webspr/ibex. The documentation for the 0.3 betas is at [Documentation03](Documentation03.md). #

# Versions #
This documentation covers Webspr 0.2.7. The 0.1.x
versions of Webspr come with a README containing full documentation.  The
latest version of this document can be found at
http://code.google.com/p/webspr/wiki/Documentation.
See the end of this document for the changelog.

# Requirements #
  * Python >= 2.3.
  * The `paste` module for Python if you want to run the stand-alone server.

# Introduction #
Webspr allows you to run various kinds of psycholinguistic experiment online.
(Originally only self-paced reading was supported, hence the name.)  The system
is modular and the range of possible experiments is steadily growing. Webspr
uses JavaScript and HTML only, and doesn't require the use of plugins such as
Java or Flash.

# Setting up the server #
There are two ways of running the server: either as a stand-alone HTTP server
or as a CGI process. By default, the server runs in stand-alone mode. To start
it, change to the `www` directory and execute server.py:
```
    python server.py
```
This will start the server on port 3000 by default (so you can find the
experiment at http://localhost:3000/experiment.html).

**Note:** you will need to
have the `paste` module installed for Python in order for stand-alone mode to
work (see http://pythonpaste.org). The CGI mode requires only modules that come
with the standard Python 2.3/2.4/2.5 distribution.

The stand-alone server is limited to serving files relating to Webspr, so it is
unlikely to be useful for real work (unless you hide it behind a proxy).
However, it is useful for testing experimental designs without setting up a
real HTTP server, and for running experiments offline.

The server can be configured by editing `server_conf.py`. Each of the options
is commented. Change the `SERVER_MODE` variable to determine whether the server
runs in stand-alone mode or as a CGI application. When `SERVER_MODE` is set to
"cgi", `server.py` will work as a standard CGI program; when it is set to
"paste", the server will run in stand-alone mode. You can change the value of
`PORT` to determine the port the server will listen on when operating in
stand-alone mode. The `-m` and `-p` command-line options can also be used to
set the server mode and port respectively. These options override those set in
`server_conf.py`.

If you are running the server as a CGI application, make sure that the
web server you are using can serve up `experiment.html` as a static file. All
dynamic requests go through `server.py`, so as long as `experiment.html` can be
accessed, and the server recognizes `server.py` as a CGI application,
everything should be fine. The "Step-by-step CGI" section below goes through
the process of setting up webspr as a CGI app in detail.

The directories `js_includes`, `data_includes` and `css_includes` contain
JavaScript (the first two) and CSS (the last one) files required for
particular kinds of experiment. When an HTTP request is made for
`server.py?include=js`, `server.py?include=data` or `server.py?include=css`,
the server concatenates all the files in the specified directory and serves up
the result. Your data file(s) will live in `data_includes`.

The server stores some state in the `server_state` directory. This
directory is automatically created by the server if it does not
already exist, and in order to start the server from a fresh state you
may simply delete this directory and/or its contents. Currently, the
directory just contains the counter used to alternate latin square
designs (see "Latin Square Designs" section below). This counter can
be reset on server startup using the `-r` option.

The server logs messages in the file `server.log`. The default is to store all
files in the same directory as `server.py` (i.e. logs, results, the
`server_state` directory, etc.), but the working directory of the server can be
modified by setting the variable `WEBSPR_WORKING_DIR` in `server_conf.py`. You
can also set the environment variable of the same name.  (The value of the
environment variable overrides the value of the variable in `server_conf.py`.)

On Linux/Unix/OS X, the server uses file locking to ensure that the results
file and server state remain consistent. Currently, it does not do so on
Windows, so there is a theoretical possibility of the server state or the results
being corrupted if you run the server in a Windows environment (but unless you
have very high traffic, it's purely theoretical).

The stand-alone server has been tested on Windows and OS X (but will almost
certainly work on any system with Python 2.3/2.4/2.5, so long as the `paste` module
is installed). The CGI server has been tested on OS X and Linux using the
lighttpd web server in both cases.

## Step-by-step CGI ##
This subsection describes how to set up webspr as a CGI application from
scratch.  Since the particulars of different web servers differ, some parts are
necessarily rather vague. There are many possible ways of organizing the
files/directories; the setup described below is just the simplest.

**Step 1:** Ensure that the `www` directory is somewhere within the root
directory of your HTTP server. You may want to place the entire `webspr`
directory within the root directory, or you may want to copy the files in `www`
to a new location within the root directory. All of these files are ordinary
static files except for `server.py`, which needs to be run as a CGI app.

**Step 2:** Decide on a location for the main webspr directory. Depending on the
details of your setup, you may be able to leave it in place, or you may need to
copy it to a directory which the HTTP server has permission to access (so that
`server.py` may access files in this directory when it is executed).

**Step 3:** Edit `server.py` and change the value of
`SERVER_CONF_PY_FILE` to point to the new location of server\_conf.py.

**Step 4:** Edit `server_conf.py` and change the value of
`WEBSPR_WORKING_DIR` to the new location of the main `webspr` dir.

**Step 5:** Edit `server_conf.py` and change change the value of
`SERVER_MODE` to `"cgi"`.

**Step 6:** If the version of Python you wish to use is not the default used by
the HTTP server, add a `#!` line at the beginning of `server.py`.

Once these steps are complete, it's just a matter of configuring your HTTP
server correctly. If you are using shared hosting, there is a reasonably good
chance that the HTTP server will already have been configured to run Python CGI
apps, in which case you won't need to do any additional configuration. There is
an example configuration file for lighttpd included in the distribution
(`example_lighttpd.conf`).

# Basic concepts #
A Webspr experiment is essentially a sequence of _items_.
Each item is itself a sequence of _entities_. To give a concrete example, each
item in a self-paced reading experiment might consist of two entities: an
entity providing a sentence for the subject to step through word by word,
followed by an entity posing a comprehension question. Some other items and
entities would also be present under most circumstances. For example, there
would probably be a "separator" entity between each sentence/question pair in
order to provide a pause between sentences. Schematically, the sequence of
items would be as follows (the Wiki insists on displaying this in pretty
colors):
```
ITEM 1:
    ENTITY 1: Sentence
    ENTITY 2: Comprehension question
ITEM 2:
    ENTITY 1: Pause for two seconds
ITEM 3:
    ENTITY 1: Sentence
    ENTITY 2: Comprehension question
ITEM 4:
    ENTITY 1: Pause for two seconds
ITEM 5:
    ENTITY 1: Sentence
    ENTITY 2: Comprehension question
```
It is not necessary to construct the full sequence of items and entities
manually. Webspr provides tools for ordering items in various ways (e.g. for
inserting a pause between each item) and for implementing latin square designs.
More on these shortly.

Each entity is an instance of a _controller_, which determines the kind of
experimental task that the entity will present.  For example, there is a
`DashedSentence` controller useful for self-paced reading and speeded
acceptability judgment tasks.  Webspr has a modular design, where each
controller is a JavaScript object that follows a standard interface. This
makes it quite easy to add new controllers if you are familiar with
JavaScript/DHTML programming.

Webspr stores results in CSV format. This makes it easy to import results into
spreadsheets, Matlab, R, etc. Each entity may contribute zero, one **or more**
lines to the results file. The first seven columns of each line give generic
information about the result (e.g. the MD5 hash of the subject's IP address) and
the rest give information specific to the particular element (e.g. word reading
times, comprehension question answers). The first seven columns are as follows:

| **Column** | **Information**                                                  |
|:-----------|:-----------------------------------------------------------------|
| 1          | Time results were received (seconds since Jan 1 1970)            |
| 2          | MD5 hash of participant's IP address                             |
| 3          | Name of the controller for the entity (e.g. "DashedSentence")    |
| 4          | Item number                                                      |
| 5          | Element number                                                   |
| 6          | Type                                                             |
| 7          | Group                                                            |

Note that some information pertaining to an entire experiment (e.g. the time
that the server received the results, the MD5 hash of the IP address) is
duplicated on each line of the results. This often makes it easier to parse the
results, though it makes the format much more verbose.  The significance of the
"type" and "group" columns will be explained later; they are involved in
specifying the ordering of items.

There are two ways to find out what the values in each column mean.  The
"manual" method is to interpret the first seven columns of each line as
specified above, and then to consult the documentation for the relevant
controllers to determine the format of the subsequent columns. All of the
controllers that are bundled with the Webspr distribution are fully documented
here.  An easier method is to look at the comments in the results file: for
each sequence of lines in the same format, the server adds comments describing
the values contained in each column.

**Important**: A single element my contribute multiple lines to the results file.
For example, if the `DashedSentence` element is in "self-paced reading" mode, it
will add a line to the results file for every word reading time it
records. Thus, there is not a one-to-one correspondence between items/elements
and lines.

**New:** The server now uses a more sophisticated algorithm for commenting lines in
the results file. It is now able to handle cases where there are repeating
patterns of lines in a results file.

# Format of a data file #
Data files for Webspr are JavaScript source files, but it is not really
necessary to know JavaScript in order to write one.  The most important part
of a data file is the declaration of the "items" array, as in the following
example:
```
var items = [

["filler", DashedSentence, {s: "Here's a silly filler sentence"}],
["filler", DashedSentence, {s: "And another silly filler sentence"}],
["relclause", DashedSentence, {s: "A sentence that has a relative clause"}],
["relclause", DashedSentence, {s: "Another sentence that has a relative clause"}]

]; // NOTE SEMICOLON HERE
```
The "items" array is an array of arrays, where each subarray specifies a single
item. In the example above, every item contains a single element (multiple
element items will be covered shortly).

  * The first member of each subarray specifies the _type_ of the item.  Types can either be numbers or strings. Although the types in the example above have descriptive names, Webspr does not interpret these names in any way.

  * The second member specifies the controller.

  * The third member is an associative array of key/value pairs. This array is passed to the controller and is used to customize its behavior. In this case, we pass only one option ("s"), which tells the `DashedSentence` controller which sentence it should display.

Once the items array has been created, Webspr must be told the order in which
the items should be displayed. There are some moderately sophisticated
facilities for creating random orderings and latin square designs, but for the
moment, let's just display the items in the order we gave them in the array.
This can be achieved by adding the following definition (which won't make much
sense yet):
```
var shuffleSequence = seq(anyType);
```

Suppose we wanted to pair each sentence with a comprehension question.  The
easiest way to do this is to add a second element to each item:
```
var items = [

["filler", DashedSentence, {s: "Here's a silly filler sentence"},
           Question, {q: "Is this a filler sentence?", as: ["Yes", "No"]}],
["filler", DashedSentence, {s: "And another silly filler sentence"},
           Question, {q: "Does this sentence have a relative clause?", as: ["Yes", "No"]],
["relclause", DashedSentence, {s: "A sentence that has a relative clause"},
              Question, {q: "Was there movement through [Spec,CP]?", as: ["Yes", "No"]}],
["relclause", DashedSentence, {s: "Another sentence that has a relative clause"},
              Question, {q: "Was the first word of that sentence 'frog'?", ["Yes", "No"]}]

]; // NOTE SEMICOLON HERE
```
As shown above, this is done simply by adding to each item further pairs of
controllers and associative arrays of options. It is rather tiresome to have to
set the `as` option to ["Yes", "No"] every time, but this can easily be avoided
by specifying this as the default for the Question controller. To give an
example of how defaults for multiple controllers are specified, let's also set
the `mode` option of `DashedSentence` to "speeded acceptability":
```
var defaults = [
    Question, {as: ["Yes", "No"]},
    DashedSentence, {mode: "speeded acceptability"}
];
```
Once this definition is in place, we can drop the specification of the `as`
option for each Question element. The final data file looks like this:
```
var shuffleSequence = seq(anyType);

var defaults = [
    Question, {as: ["Yes", "No"]},
    DashedSentence, {mode: "speeded acceptability"}
];

var items = [

["filler", DashedSentence, {s: "Here's a silly filler sentence"},
           Question, {q: "Is this a filler sentence?"}],
["filler", DashedSentence, {s: "And another silly filler sentence"},
           Question, {q: "Does this sentence have a relative clause?"}],
["relclause", DashedSentence, {s: "A sentence that has a relative clause"},
              Question, {q: "Was there movement through [Spec,CP]?"}],
["relclause", DashedSentence, {s: "Another sentence that has a relative clause"},
              Question, {q: "Was the first word of that sentence 'frog'?"}]

];
```
**Where to put your data file**: Data files live in the `data_includes`
directory, and must have a `.js` extension. You can only have data one file in
the directory at any one time, since if you have multiple files, they will just
overwrite the definitions for `shuffleSequence`, `items` and `defaults`.
However, you can tell the server to ignore some of the files in `data_includes`
(see the section "Configuring `js_includes`, `data_includes` and `css_includes`").

# Shuffle sequences #
## `seq`, `randomize` and `shuffle` ##

A "shuffle sequence" is a JavaScript data structure describing a series of
"shuffling", randomizing and sequencing operations over an array of items.  A
variable called `shuffleSequence` should be defined in your data file with a
data structure of this sort as its value.

Shuffle sequences are composed of three basic operations, `seq`, `randomize`
and `shuffle`. Both take a series of "type predicates" as arguments, where each
type predicate is the characteristic function of a set of types. A type
predicate may be one of the following:

  * A string or integer, denoting the characteristic function of all items of the given type.

  * A JavaScript function, returning a boolean value when given a type (either a string or integer).

  * Another shuffle sequence (shuffle sequences can be embedded inside bigger shuffle sequences).

The basic operations work as follows:

  * A statement of the form `seq(pred1, pred2, pred3, ...)` specifies a sequence where all items matching `pred1` precede all items matching `pred2`, all items matching `pred2` precede all items matching `pred3`, and so on. The original relative ordering between items of the same type is preserved. A `seq` with only one argument is permissible.

  * A statement of the form `randomize(pred1)` specifies a randomly ordered sequence of all items matching pred1.

  * A statement of the form `shuffle(pred1, pred2, pred3, ...)` specifies that items matching the given predicates should be shuffled together in such a way that items matching each predicate are evenly spaced. The original relative ordering between items of the same type is preserved.

The following type predicates are predefined as JavaScript functions:

| **Function**           | **Description**                                           |
|:-----------------------|:----------------------------------------------------------|
| `anyType`              | Matches any type.                                         |
| `lessThan0`            | Matches any integer type < 0.                             |
| `greaterThan0`         | Matches any integer type > 0.                             |
| `equalTo0`             | Matches any integer type = 0.                             |
| `startsWith(s)`        | Matches any string type starting with s.                  |
| `endsWith(s)`          | Matches any string type ending with s.                    |
| `not(pred)`            | Matches anything that is not of a type matched by pred.   |
| `anyOf(p1, p2, ...)`   | Takes any number of type predicates as its arguments, and matches anything matching one of these predicates. |

If you define your own predicates, be careful to test that they are
cross-browser compatible. See the "Cross-browser compatibility"
section below for some pertinent advice.  The predicates above are
defined in `shuffle.js`.

The power of shuffle sequences derives from the possibility of composing them
without limit. Suppose we want the following order: all practice items in their
original order followed by evenly spaced real and filler items in random order.
Assuming the types "practice", "real" and "filler", we could use the following
shuffle sequence:
```
seq("practice", shuffle(randomize("real"), randomize("filler")))
```
Now suppose that there are two types of real item ("real1" and "real2"), and we
wish to order the items the same way as before:
```
seq("practice", shuffle(randomize(anyOf("real1", "real2")),
                randomize("filler")))
```
What if we also want the two types of real item to be evenly spaced?  The
following formula will do the trick:
```
seq("practice", shuffle(randomize("filler"),
                        shuffle(randomize("real1"),
                                randomize("real2"))))
```

This first shuffles items of type "real1" and items of type "real2" and then
shuffles filler items into the mix.  Finally, practice items are prepended in
the order they were given in `data.js`.

Since it is often useful to apply `randomize` to every argument of `shuffle`,
there is a utility function, `rshuffle`, which automates this. The following
equivalence holds:
```
rshuffle(a1, a2, ...) = shuffle(randomize(a1), randomize(a2), ...)
```
If no shuffle sequence is specified, Webspr uses the following default
sequence:
```
seq(equalTo0, rshuffle(greaterThan0, lessThan0))
```

This will seem rather cryptic to anyone not familiar with the behavior of
earlier versions of Webspr, where this ordering specification was built in and
unchangeable. In short, it works well if practice items have type 0, filler
items have integer types < 0, and real items have integer types > 0.

**Important**: A shuffle sequence must always have one of `seq`, `shuffle`,
`randomize` or `rshuffle` as its outer element. A single string or integer is
_not_ a valid shuffle sequence, and neither is a predicate expression such as
`not("foo")`. Thus, one must use `seq("foo")`, not just `"foo"`, and
`seq(not("foo"))`, not just `not("foo")`.

It is possible to include duplicate items in the final sequence. For example,
`seq("foo", "foo")` would include every item of type "foo" twice. For this
reason, it is possible to accidentally include duplicate items if a number of
your predicates overlap.  You can define your own shuffle sequence operators
and predicates quite easily; see `shuffle.js` for the definitions of the `seq`,
`shuffle` and `randomize` operators.

## Adding separators ##
Normally, it is a good idea to have some sort of padding in between items to
warn participants that they have finished one item and are starting another.
Webspr provides the `Separator` item for this purpose. It can either work on a
timeout or prompt for a keypress. Here's an example:
```
["sep", Separator, {transfer: 1000, normalMessage: "Please wait for the next sentence."}]
```
When the `transfer` option is set to 1000, this specifies that there should be
a 1000ms wait before the next item. The `normalMessage` option gives the
message that should be displayed if the participant didn't do anything wrong on
the previous item (see the section "Communication between elements" for more
details). If the other items have failure conditions, you should set the
`errorMessage` option too. If you want the participant to proceed by pressing a
key rather than waiting, set `transfer` to "keypress".

The shuffle sequence operator `sepWith` is provided for the purpose of
interpolating separators with other items. It takes two arguments: the first is
a shuffle sequence specifying the sequence of items which should be used to
separate the other items; the second argument is a shuffle sequence specifying
the other items.

Let's take the example data file above and add timeout Separators between each
item. There are no failure conditions in this experiment (since there is no
"wrong" answer for an acceptability judgment) so we only need to specify the
`normalMessage` option. For the moment, we'll still present the sentences in
the order in which they appear in the `items` array. Here's the modified file:
```
var shuffleSequence = sepWith("sep", not("sep"));

var defaults = [
    Question, {as: ["Yes", "No"]},
    DashedSentence, {mode: "speeded acceptability"}
];

var items = [

["sep", Separator, {transfer: 1500, normalMessage: "Please wait for the next item."}],

["filler", DashedSentence, {s: "Here's a silly filler sentence"},
           Question, {q: "Is this a filler sentence?"}],
["filler", DashedSentence, {s: "And another silly filler sentence"},
           Question, {q: "Does this sentence have a relative clause?"}],
["relclause", DashedSentence, {s: "A sentence that has a relative clause"},
              Question, {q: "Was there movement through [Spec,CP]?"}],
["relclause", DashedSentence, {s: "Another sentence that has a relative clause"},
              Question, {q: "Was the first word of that sentence 'frog'?"}]

];
```

## Manipulating individual items ##
So far, we've been treating items as atoms for the purposes of shuffle
sequences -- although an item might be composed of several elements, the
operations `seq`, `randomize` and `shuffle` ignore this internal structure.
However, it is sometimes useful to be able to append or prepend a particular
sequence of elements to every item.  For example, if you are doing a speeded
acceptability judgment task, you might want every sentence to be followed by
exactly the same question ("Was this a good sentence?"). To this end, webspr
provides the `precedeEachWith` and `followEachWith` operations.

Both functions take two arguments, each of which should be a shuffle sequence.
The first argument specifies the sequence of items which (when flattened to a
sequence of elements) is to be appended/prepended to every item in the second
argument.  Returning to the previous example data file, let's modify it so that
every sentence is followed by the same acceptability question.  We'll also
ensure that the sentences are randomly ordered, with the fillers and "real"
sentences evenly spaced:
```
var shuffleSequence = followEachWith("question", rshuffle("filler", "relclause"));

var defaults = [
    DashedSentence, {mode: "speeded acceptability"}
];

var items = [

["question", Question, {q: "Was that a good sentence?", as: ["Yes", "No"]}],

["filler", DashedSentence, {s: "Here's a silly filler sentence"}],
["filler", DashedSentence, {s: "And another silly filler sentence"}],

["relclause", DashedSentence, {s: "A sentence that has a relative clause"}],
["relclause", DashedSentence, {s: "Another sentence that has a relative clause"}]

];
```
**Important:** `precedeEachWith` and `followEachWith` have a somewhat confusing
behavior with respect to the format of the results file. Although in effect,
the first argument of `followEachWith` is appended to every item, the appended
elements are not considered a part of the items they are appended to in the
results file. Rather, every question in the preceding example will have the
same item number and element number in the results file (that based on the
position of the question item in the data file).

## Latin square designs ##
Webspr has built-in support for latin square designs. These are implemented by
assigning each item a _group_ in addition to its type. Each participant sees
only one item out of all the items in any given group. To give an example, we
could place both of the "relclause" sentences from the previous example in the
same group using the following code:
```
[["relclause", 1], DashedSentence, {s: "A sentence that has a relative clause"}],
[["relclause", 1], DashedSentence, {s: "Another sentence that has a relative clause"}]
```
Now, any given participant will see only one of these
sentences. Designs are rotated using a counter stored on the
server. This mechanism requires the participant to have cookies enabled;
otherwise, a random counter will be used. Groups, like types, may either be strings or numbers. By
default, webspr does not check that all groups contain the same number
of items (this behavior is new in 0.2.4). You can set the
`equalGroupSizes` variable to `true` in order to revert to the old
behavior, where an error is raised if groups contain differing number
of items. (See the "Miscellaneous options" subsection below.)

**New:** You may now choose which latin square a participant will be placed in
by using a URL of the following form: ".../server.py?withsquare=XXXX". This
will set the latin square to XXXX for the current participant and then redirect to ".../experiment.html".
Selecting the latin square in this manner does **not** modify the master counter stored on the server.
Again, cookies are required for this feature to work, and if the participant does
not have cookies enabled a random counter will be used.

A new (and not very well-tested) feature allows for more complex designs where
selection of an item from one group is dependent on selection of an item from
another. For example, you can specify that the item chosen from group 3 should
be the same as the item chosen from group 2 (i.e. if the first item is chosen
from group 2, the first item will also be chosen from group 3). To use this
feature, just replace each group specifier with a pair of group specifiers,
where the first member of the pair is the original group specifier, and the
second is the group which governs selection from the original group.  For
example, suppose that we have another group (group 2), and we want choices from
this group to be linked to choices from group 1 in the example above.  The
following code will do the trick:
```
[["relclause", [2, 1]], DashedSentence, {s: "I am paired with 'A sentence that has a relative clause'"}],
[["relclause", [2, 1]], DashedSentence, {s: "I am paired with 'Another sentence that has a relative clause'"}]
```
Note that the second number in the pair must be the same for all items in the group.
**Warning:** This feature may be removed in future releases if I get around to implementing
a more general way of implementing more complex latin square designs.

# Communication between elements #
Webspr allows for a limited amount of communication between elements.  Each
element may set keys in a hashtable which is passed to the next element.  The
hashtable is cleared between elements, so there is no possibility of
long-distance communication.

Currently, this system is used to provide feedback to participants when they
(for example) answer a comprehension question incorrectly.  Controllers such as
`Question` set the key "failed" if something goes wrong, and the next
`Separator` item is then able to display a message warning the participant that
they answered incorrectly.

# Controllers #
## Separator ##
**Options**

| **Option**        | **Default**    | **Description** |
|:------------------|:---------------|:----------------|
| transfer          | `"keypress"`   | Must be either `"keypress"` or a number. If the former, participant goes to the next item by pressing any key. If the latter, specifies number of ms to wait before the next item. |
| normalMessage     | `"Press any key to continue."` | Message to display if the previous item was completed normally. |
| errorMessage      | `"Wrong. Press any key to continue."` | Message to display (in red) if the previous item was not completed normally (e.g. timeout, incorrect answer). |
| ignoreFailure     | `false`        | If true, never displays an error message. |

**Results**

`Separator` does not add any lines to the results file.

## Message ##
**Options**

| **Option**            | **Default**    | **Description**                                                        |
|:----------------------|:---------------|:-----------------------------------------------------------------------|
| html                  | _obligatory_   | The HTML for the message to display (see section "HTML Code" below).   |
| hideProgressBar       | `true`         | If true, the progress bar is hidden when the message is displayed.     |
| transfer              | `"click"`      | Either `"click"`, `"keypress`" or an integer. If `"click"`, the participant clicks a link at the bottom of the message to continue (see "continueMessage" option). If `"keypress"`, they press any key to continue. If an integer, the experiment continues after pausing for the specified number of milliseconds. |
| requiresConsent       | `false`        | If true, the participant is required to tick a checkbox indicating that they consent to do the experiment (in this case, the message would probably be some sort of statement of terms/conditions). This option can only be set to `true` if the "transfer" option is set go `"click"`. |
| continueMessage       | `"..."`        | Only valid if the "requiresConsent" option is set to `"true"`. This specifies the text that will appear in the link that the participant needs to click to continue with the experiment. |
| consentMessage        | `"..."`        | Only valid if the "requiresConsent" option is set to `"true"`. This specifies the text that will appear next to the checkbox. |
| consentErrorMessage   | `"..."`        | Only valid if the "requiresConsent" option is set to `"true"`. This specifies the error message that will be given if the participant attempts to continue without checking the consent checkbox. |

**Results**

`Message` does not add any lines to the results file.

## DashedSentence ##
**Options**

| **Option**      | **Default**              | **Description**                                               |
|:----------------|:-------------------------|:--------------------------------------------------------------|
| s               | _obligatory_             | The sentence. This is either a string, in which case the sentence will be presented word-by-word, or a list of strings ("chunks"), in which case the sentence will be presented chunk-by-chunk. If one of the words/chunks begins with the character "@", then the controller will finish after the word beginning with "@" is displayed (the "@" will be stripped when the word is presented). This feature can be useful if you want (for example) to interrupt a self-paced reading item with a lexical decision task. |
| mode            | `"self-paced reading"`   | Either `"self-paced reading"` or `"speeded acceptability"`.   |
| wordTime        | `300`                    | If mode is `"speeded acceptability"`, the time in ms each word should be displayed for. |
| wordPauseTime   | `100`                    | If mode is `"speeded acceptability"`, the time in ms a word should remain blank before it is shown. |
| sentenceDescType | `"literal"`              | Determines the format of column 1 of the results (see table below). If `"md5"`, column contains hex digest of md5 hash of sentence. If `"literal"`, column contains the sentence itself (encoded as a URL with %XX escapes). Earlier versions of webspr did not have this option and always stored md5 hashes. **Important:** The use of md5 hashes is not recommeded if you are using non-ASCII strings, since different browsers give inconsistent md5 hashes in this case! |

**Results**

The format of the results depends on the setting of the `mode` option. If it is
set to "speeded acceptability", results have the following format:

| **Column** | **Description** |
|:-----------|:----------------|
| 1          | See documentation for 'sentenceDescType' option above. |

If `mode` is set to "self-paced reading", the results look like this:

| **Column** | **Description** |
|:-----------|:----------------|
| 1          | Word number. For example, "1" indicates that this line gives the time it took to read the first word (i.e. the difference between <the time at which the first word appeared> and <the time at which it disappeared and the second word appeared>). |
| 2          | The word.       |
| 3          | The reading time in ms. |
| 4          | Either 1 or 0. Indicates whether or not there was a line break between word n and word n + 1 (where reading time is for word n). |
| 5          | See documentation for 'sentenceDescType' option above. |

## FlashSentence ##
**Options**

| **Option** | **Default**    | **Description**                 |
|:-----------|:---------------|:--------------------------------|
| s          | _obligatory_   | The sentence to be displayed.   |
| timeout    | 2000           | If `null`, the sentence is displayed indefinitely (only useful if part of a VBox). Otherwise, a number giving the time in ms to display the sentence.    |
| sentenceDescType | `"md5"`        | See documentation for DashedSentence controller. |

**Results**

| **Column** | **Description** |
|:-----------|:----------------|
| 1          | See documentation for 'sentenceDescType' option of the DashedSentence controller. |

## Question ##
**Options**

| **Option**       | **Default**    | **Description**                                                     |
|:-----------------|:---------------|:--------------------------------------------------------------------|
| q                | `null`         | The question to pose.                                               |
| as               | _obligatory_   | A list of strings giving the answers the user has to choose from.   |
| instructions     | `null`         | Instructions for answering the question, displayed following the question and the answer selection. |
| hasCorrect       | `false`        | If `false`, indicates that none of the answers is privileged as correct. Otherwise, is either `true`, indicating that the first answer in the `as` list is the correct one; an integer, giving the index of the correct answer in the `as` list (starting from 0); or a string, giving the correct answer. |
| showNumbers      | `true`         | If `true`, answers are numbered and participants can use number keys to select them. |
| randomOrder      | `true` if the question has a correct answer, false otherwise. | Whether or not to randomize the order of the answers before displaying them. |
| presentAsScale   | `false`        | If `true`, answers are presented as a scale (useful for acceptability ratings). If any of the points in the scale are integers 0-9, the participant may select them by pressing a number key. |
| leftComment      | `null`         | _Only valid if `presentAsScale` is `true`._ This option specifies text to be displayed at the left edge of a scale (e.g. "Bad"). |
| rightComment     | `null`         | As for "leftComment", but for the right edge of the scale.          |
| timeout          | `null`         | If `null`, there is no time limit. Otherwise, should be a number giving the time in ms a participant has to answer the question. |

**Results**

| **Column** | **Description** |
|:-----------|:----------------|
| 1          | The question that was posed (encoded as a URL with %XX escapes). |
| 2          | The answer that the participant gave (also encoded as a URL).    |
| 3          | "NULL" if the question as no correct answer. Otherwise, 1 if the participant answered correctly, or 0 if they didn't. |
| 4          | The time the participant took to answer the question (ms). |

## AcceptabilityJudgment ##
| **Option**       | **Default**           | **Description**                |
|:-----------------|:----------------------|:-------------------------------|
| s                | _obligatory_          | The sentence.                  |
| q                | _obligatory_          | The question.                  |
| as               | _obligatory_          | Answers (as for `Question`).   |
| hasCorrect       | `false`               | As for `Question`              |
| showNumbers      | `true`                | As for `Question`              |
| randomOrder      | _as for `Question`_   | As for `Question`              |
| presentAsScale   | `false`               | As for `Question`              |
| leftComment      | `null`                | As for `Question`              |
| rightComment     | `null`                | As for `Question`              |
| timeout          | `null`                | As for `Question`              |

**Results**

Each `AcceptabilityJudgment` adds **two** lines to the results file. The first
line is the same as for the `FlashSentence` controller; the second line is the
same as for the `Question` controller.

## VBox ##
The `VBox` controller makes it possible to combine multiple controllers to form
a single controller. Each controller in the VBox is displayed at the same time,
one on top of the other. This allows the functionality of simple controllers to
be reused in the construction of more complex controllers. For an example of a
controller constructed using a VBox, see
`js_includes/acceptability_judgment.js`. For simpler cases, you can just create
a VBox directly in your data file instead of creating a new controller in the
`js_includes` directory.

**Options**

| **Option**  | **Default**    | **Description** |
|:------------|:---------------|:----------------|
| children    | _obligatory_   | An array of child controllers. Has exactly the same format as an array of elements for an item |
| triggers    | _obligatory_   | In order to determine when a VBox element is complete, you must give an array of the indices of those of its children which are "triggers" (indices start from 0). When each of the trigger elements is complete, the VBox is complete. |
| padding     | `"2em"`        | The amount of vertical padding to place between the children. This should be a CSS dimension. |

**Results**

The `VBox` controller simply concatenates the results of its children in the order that the children were given.

# Further configuration #
## Miscellaneous  options ##
You can set the values of the following variables in your data file (e.g. `var showProgressBar = true;`).

| **Option** | **Default** | **Description** |
|:-----------|:------------|:----------------|
| `showProgressBar` | `true`      | Whether or not to show a progress bar. |
| `pageTitle` | `"experiment"` | Page title.     |
| `sendingResultsMessage` | `"..."`     | The message shown while results are being sent to the server. |
| `completionMessage` | `"..."`     | The message shown when the results are successfully sent to the server. |
| `completionErrorMessage` | `"..."`     | The message shown when there is an error sending the results to the server. |
| `practiceItemTypes` | `[]`        | A list of types for practice sentences. A sentence whose type is in this list will have a blue "practice" heading above it. |
| `showOverview` | false       | See "Overviews" section |
| `centerItems` | true        | Whether or not items should be centered on the page. |
| `equalGroupSizes` | false       | If true, groups in latin square designs are required to contain equal numbers of items. |

## Configuring `js_includes`, `data_includes` and `css_includes` ##
The directories `js_includes`, `data_includes` and `css_includes` directories
contain JavaScript and CSS files that are necessary for the running of an
experiment.  The most important of these is the data file in `data_includes`
containing the list of items for the experiment, but each controller also has
its own file in `js_includes` (for example, the `DashedSentence` controller
lives in `dashed_sentence.js`).  Many controllers also define some CSS classes
in corresponding files in `css_includes` (e.g. `dashed_sentence.css`). If you
write your own controllers, you need to put the JavaScript and CSS files in
these directories.

When the webpage for an experiment is accessed, the server concatenates all the
files in `js_includes` and serves them up as a single file (ditto for
`data_includes` and `css_includes`). You can tell the server to ignore some of
the files in `js_includes` and `css_includes` by editing the variables
`JS_INCLUDES_LIST`, `DATA_INCLUDES_LIST` and `CSS_INCLUDES_LIST` in
`server_conf.py`.  (There is a comment documenting how to do this.) You may
wish to exclude JavaScript and CSS files which are not used by your experiment
in order to reduce the size of the file that needs to be downloaded. Since the
files in both directories are named after the controllers with which they are
associated, it is easy to see which files are superfluous.

**However:** note that the file `main.css` is required by all
controllers.

# HTML Code #
Webspr provides two ways of passing HTML code to the `Message` controller
(currently the only controller which has an `html` option). The first is simply
to pass a JavaScript string containing the HTML code. The second is to pass a
JavaScript data structure representing the HTML Code. For example, here is
the representation of a `div` element containing two paragraphs:
```
["div",
    ["p", "This is the first paragraph."],
    ["p", "This is the second paragraph.", "Containing two text nodes."]
]
```
Note that a space will automatically be inserted between the two text nodes in
the second paragraph. If you wanted to set the foreground color of the `div` to
red, you could use the following code:
```
[["div", {style: "color: red;"}],
    ["p", "This is the first paragraph."],
    ["p", "This is the second paragraph.", "Containing two text nodes."]
]
```
If you want to set DOM properties directly, you can use
a key beginning with "@":
```
[["div", {"@style.color": "red"}],
    ["p", "This is the first paragraph."],
    ["p", "This is the second paragraph.", "Containing two text nodes."]
]
```
Elements (e.g. `&ldquo;` -- a left double quote) are specified as in the
following example:
```
[["div", {"@style.color": "red"}],
    ["p", "This is the first paragraph."],
    ["p", "This is the second paragraph.", "Containing two text nodes."],
    ["p", "Here's a paragraph where ", ["&ldquo;"], "this", ["&rdquo;"], " is quoted."]
]
```
Spaces are _not_ automatically inserted before and after elements.

# Overviews #
Sometimes it's useful to get an overview of the sequence of items in an
experiment without actually running through each item. There are two ways of
getting webspr to display an overview of this sort. The first is to add the
statement `var showOverview = true;` to your data file.  The second is
to go to the page `overview.html` instead of `experiment.html`.

# Creating your own controllers #
This is quite easy if you are familiar with JavaScript/DHTML.
As an example, here's the code for an older (and simpler) version of the
`Message` controller:
```
Message.name = "Message";
Message.obligatory = ["html"];
Message.countsForProgressBar = false;

function Message(div, options, finishedCallback, utils) {
    this.div = div;
    this.options = options;
    this.hideProgressBar = dget(options, "hideProgressBar", true);

    this.html = options.html;
    div.className = "message";
    div.appendChild(htmlCodeToDOM(this.html));

    this.transfer = dget(options, "transfer", "keypress");
    assert(this.transfer == "keypress" || typeof(this.transfer) == "number",
           "Value of 'transfer' option of Message must either be the string 'keypress' or a number");

    if (this.transfer == "keypress") {
        this.handleKey = function(code, time) {
            finishedCallback(null);
            return true;
        }
    }
    else {
        utils.setTimeout(finishedCallback, this.transfer);
    }
}

Message.htmlDescription = function (opts) {
    var d = htmlCodeToDOM(opts.html);
    return truncateHTML(d, 100);
}
```
The first three lines set some properties of the `Message` class.
The `obligatory` option specifies those options which must obligatorily be
given to the controller. In this case, it is obligatory that the controller
be given an `"html"` option. Both `Controller.name` and `Controller.obligatory`
must be set. The `countsForProgressBar` property is optional and is `true`
by default. It determines whether instances of the controller count towards
the size of the progress bar.

The constructor for the controller class is called with four arguments:

  * The `div` which the controller should use to display HTML in.
  * The options which the controller was given (an object).
  * A function which should be called with lines to be added to the results file when the controller is complete.
  * A "utils" object which contains some useful functions.

In the case of `Message`, `finishedCallback` is called with `null` as its argument
because this controller does not add any lines to the results file.
In general, the format of a non-null argument to `finishedCallback` is as follows:
```
[
    // Line 1.
    [ ["fieldname1", value1], ["fieldname2", value2], ["fieldname3", value3], ... ],
    // Line 2.
    [ ["fieldname2", value2], ["fieldname2", value2], ["fieldname3", value3], ... ],
    ...
]
```

As can be seen in the code for `Message`, the `utils` object provides a `setTimeout` method
similar to the builtin `setTimeout` function of JavaScript.
Any timeouts set using this method are automatically cleared when the controller is complete.

# Cross-browser compatibility #
I have tested compatibility with the following browsers:

  * Internet Explorer 5.5, 6 and 7.
  * Firefox 1, 1.5, 2, and 3.
  * Safari 3.
  * Opera 9 (latest point release).

Known cross-browser issues:

  * Overviews (see previous section) currently do not work on all versions of Internet Explorer.

  * Pressing '6' and '7' in Opera affects text size; this interacts badly with acceptability judgments on scales including 6 and 7. I have not yet found a way of preventing Opera from interpreting these keypresses.

  * The stand-alone server serves up the JavaScript and CSS include files with a `Pragma: nocache` so that any changes you make will be immediately reflected if you refresh `experiment.html`. However, some versions of Internet Explorer ignore this pragma (I think this is a bug in IE, but not 100% sure yet), so you will need to delete your temporary internet files and then refresh. This is not such a big issue for live experiments, but it makes developing and testing experiments using IE a big PITA. The obvious workaround is simply not to use IE for these purposes.

# Terminological clarifications #
Unfortunately, the terms I've used relating to the design of experiments (latin squares, etc.) are enormously confusing as they use some non-standard terms, and make non-standard use of some standard terms. Specifically:

**The term 'item number' is used to describe the number assigned to a controller based on its position in the list of controllers in the data file. Of course, controllers are not normally in one-to-one correspondence with 'items' in the usual sense of the term.**

**The term 'group' is used to refer to what are usually called items (i.e. sets of conditions).**

# Known problems and issues #
The following are some subtle problems which can often arise when writing a
data file:

  * A missing comma in the list of sentences in data.js can cause highly obscure JavaScript errors with no obvious relation to their source.

  * Some browsers accept trailing commas in JavaScript array literals (i.e. they accept [1,2,3,4,] as a fine array); others do not. If your browser of choice accepts array literals of this form, be sure to check that your data.js has no trailing commas so that there will be no browser incompatibilities. It is quite easy to introduce trailing commas by accident if you comment out some of the items in the `items` array.

Setting the value of HTML options (for example the `html` option of the
`Message` controller) can be a bit of a pain, since writing HTML code inside
JavaScript string literals is a bit finicky.
(Note that there is now an alternative to using a raw HTML string;
see the "HTML Code" section above.)
If you do decide to use a raw HTML string, remember to escape singe/double
quotes with a backslash (depending on whether you enclose the string in
single/double quotes) and to escape newlines with a backslash also (by making
the backslash the last character of the line). Some browsers may accept
JavaScript string literals containing unescaped newlines, but most will not,
so make sure you don't use them.

Most browsers allow strings to be indexed using square brackets (i.e. `"foo"``[1]`
`== "f"`). Internet Explorer, however, requires the use of the string's `charAt`
method.

For debugging, I recommend using Firefox's JavaScript console. Most syntax
errors in a data file will result in an alert popping up with a warning that the
`items` array has not been defined. You can usually get a much more informative
error message by looking at the JavaScript console.

# Changes #
Changes betwen 0.2.7 (current version) and 0.2.6:
  * Server now attempts to do the Right Thing with unicode. Earlier versions would occasionally fail to work when the server was running on Windows due to crufty unicode issues. This should now be fixed.
  * `FlashSentence`, `DashedSentence` and `Question` controllers now consistently store questions/sentences in the results file in URL-encoded format.
  * Cleaned up example data file a little.
  * Fixed bug where numbers for numbered answers to comprehension questions were not displayed in IE <= 6.
  * Minor CSS fixes.

Changes between 0.2.6 and 0.2.5:
  * Fixed bug which caused sentences not be be stored in results file under some circumstances.

Changes between 0.2.5 and 0.2.4:
  * Option to store whole sentences in results file for DashedSentence and FlashSentence controllers instead of MD5 hashes (this is now the default).
  * Latin square can now be selected in the URL (".../server.py?withsquare=XXXX"); this sets the counter to XXXX and then redirects to ".../experiment.html". Selecting latin squares in this way does not alter the master counter stored on the server.

Changes between 0.2.4 and 0.2.3:
  * Bug fixes in code for processing structured HTML (see "HTML Code" section above).
  * Groups in Latin Square designs are no longer required to have equal numbers of sentences (though enforcement of this requirement can still be turned on by setting an option).
  * Minor usability improvements for consent checkboxes (can now click text next to checkbox as well as checkbox itself).

Changes between 0.2.3 and 0.2.2:
  * Add option to use "click here to continue" as well as "press any key to continue" in `Message` controller.
  * Add option for consent checkboxes to `Message` controller.
  * CGI server now works on Python 2.3 (previously required Python2.5, contrary to documentation, which incorrectly stated that it would run on Python >= 2.4).
  * Improve wording in some parts of this manual.

Changes between 0.2.2 and 0.2.1:
  * Better algorithm for commenting results in results files.
  * `FlashSentence` controller now adds a line with the MD5 of the sentence to the results file whether or not it finishes. (In practice, this means that sentence MD5s are stored when using the `Question` controller.)
  * `DashedSentence` controller now stores words as well as word numbers in results file when operating in "self-paced reading" mode.

Changes between 0.2.1 and 0.2:

  * Fix error in documentation for `FlashSentence` controller.
  * Fix bug that caused results to be recorded improperly under some circumstances.