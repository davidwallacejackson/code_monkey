Creating and Applying Changes
=============================

Once you've found some interesting Nodes, you can generate changes to the
underlying code and apply them to the project.

Here's how that works:

1.  Create a ChangeSet object (``code_monkey.edit.ChangeSet``). This tracks
    a collection of changes and prevents conflicts.
2.  Create Change objects, which specify a region of code to overwrite or
    append to, and what new code should go there.
3.  Add Changes to your ChangeSet (if two changes overlap, this will raise
    an exception).
3.  Preview your changes using ``ChangeSet.diff()``.
4.  Apply your changes to the filesystem using ``ChangeSet.commit()``.

Creating Change objects by hand would be extremely tedious, so we've got a
bunch of helpers on every Node to generate them. They live under the Node's
``.change`` property.

Here's what it looks like in action -- we'll make some edits to the code_monkey
test project::

    from code_monkey.node_query import project_query
    from code_monkey.edit import ChangeSet

    q = project_query('./test_project')

    # select every class in the project
    targets = q.flatten().classes()

    changeset = ChangeSet()

    for class_node in targets:
        changeset.add(class_node.change.inject_at_body_line(0,
            '    foo = "bar"\n'))

    print(changeset.diff())

The output, then is a typical diff::

    Changes:

    --- ./test_project/lib/edge_cases.py
    +++ ./test_project/lib/edge_cases.py
    @@ -6,6 +6,7 @@
             Underground,
             CanHire,
             ProducesPonkeys):
    +    foo = "bar"
         pass #Lair body starts here
     
     #multiline function signature
    @@ -25,4 +26,5 @@
     
     #uses dots (a 'getattr node') when specifying parent class
     class WeirdSubclass(datetime.datetime):
    +    foo = "bar"
         pass #WeirdSubclass body starts here--- ./test_project/lib/employee.py
    +++ ./test_project/lib/employee.py
    @@ -2,6 +2,7 @@
     from test_project import settings
     
     class Employee(object):
    +    foo = "bar"
     
         def __init__(self, first_name, last_name):
             self.first_name = first_name
    @@ -13,6 +14,7 @@
     
     
     class CodeMonkey(Employee):
    +    foo = "bar"
         """He writes code."""
         def __init__(self, *args, **kwargs):
             super(CodeMonkey, self).__init__(*args, **kwargs)


If you're happy with your changes, you can apply them by changing the last
line from ``print(changeset.diff())`` to ``changeset.commit()``.

The ChangeGenerator API
-----------------------

Most of the actual power here is in the ``.change`` property, which is an
instance of the ``code_monkey.change.ChangeGenerator`` class. ChangeGenerators
contain a variety of methods that return ``Change`` objects representing common
transformations. Here's everything that ChangeGenerator can do:

.. autoclass :: code_monkey.change.ChangeGenerator
    :members:


Change Objects
--------------

If there's something particularly finnicky that you can't do with ``.change``,
you can always create Change objects by hand (that's all that
ChangeGenerator does). The API is:

.. autoclass :: code_monkey.change.Change

Note that you can insert without overwriting by making the ``start`` and
``end`` parameters the same.
