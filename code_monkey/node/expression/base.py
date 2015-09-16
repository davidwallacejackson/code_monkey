from code_monkey.end_detection import EndDetector
from code_monkey.node.source import SourceNode
from code_monkey.utils import line_column_to_absolute_index

class ExpressionNode(SourceNode):
    '''Node representing an expression -- something that, when exectued,
    resolves to a value.'''

    @property
    def _source_lines(self):
        '''Return the source of every line this expression exists on (not just
        the source of the expression itself.

        We need this to use with the tokenizer -- we can't just start where the
        expression does.'''
        start_line = self._astroid_object.fromlineno - 1
        end_line = self._astroid_object.tolineno

        source = self.get_file_source_code()

        start_line_index = line_column_to_absolute_index(
            source,
            start_line,
            0)

        if end_line == source.count('\n') + 1:
            #we're at the end of the source
            end_line_index = len(source)
        else:
            end_line_index = line_column_to_absolute_index(
                source,
                end_line,
                0)

        return self._get_source_region(start_line_index, end_line_index)

    @property
    def detector(self):
        '''EndDetector representing the expression. See end_detection.py for
        details.'''

        lines = self._source_lines

        detector = EndDetector(lines)
        detector.discard_before(self._astroid_object.col_offset)

        self.consume_expression(detector)
        detector.lock()

        return detector

    def consume_expression(self, detector):
        '''Gets a detector that's been set up, but not locked. This is a hook,
        and subclasses should use it to tell the detector what to consume.'''
        raise NotImplementedError()

    @property
    def end_line(self):
        #astroid can't get this, so we parse it out using the EndDetector
        #(which gives us a line number relative to where the
        #expression **started**, hence adding self.start_line).
        return self.start_line + self.detector.last_consumed['end'][0]
  
    @property
    def end_column(self):
        #similar to end_line, but we don't need to add anything
        #(because columns reset on each line)
        return self.detector.last_consumed['end'][1]
