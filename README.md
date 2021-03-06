code_monkey
===========

code_monkey is a refactoring and code intelligence tool for Python
projects. It builds a tree representing your project, then provides an easy API
for querying nodes out of the tree. Once you've found the nodes you're looking
for, you can generate changes and apply them to your whole project at once.

Full documentation is available [here](http://code-monkey.readthedocs.org/en/latest/).

Usage
-----

For instance, let's say you wanted to add a certain line to every test class in
your project:

```python
    from code_monkey.node_query import project_query
    from code_monkey.edit import ChangeSet

    q = project_query('/path/to/my/project')
    test_classes = q.flatten().classes().path_contains('tests')
    changeset = ChangeSet()

    for node in test_classes:

        changeset.add(
            node.change.inject_at_body_line(1, '    foobar = 42\n'))

    changeset.commit()
```

code_monkey can also extract the value of some variables (anything that is
composed of Python literals), make changes, and write it back to the node. To
add a new fixture to your test classes, for example:

```python
    q = project_query('/path/to/my/project')
    test_classes = q.flatten().classes().path_contains('tests')
    fixture_lists = test_classes.flatten().assignments()

    changeset = ChangeSet()

    for node in fixture_lists:

        fixtures = node.eval_body()
        fixtures.append('new_fixture_name')
        fixtures = sorted(fixtures)
        changeset.add(
            node.change.value(fixtures))

    changeset.commit()
```
