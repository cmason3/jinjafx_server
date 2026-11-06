import { EditorView } from 'codemirror';
import { highlightSelectionMatches } from '@codemirror/search';
import { indentUnit, syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';
import { indentWithTab, history, defaultKeymap, historyKeymap } from '@codemirror/commands';
import { lineNumbers, highlightActiveLineGutter, drawSelection, highlightActiveLine, highlightTrailingWhitespace, keymap } from '@codemirror/view';
import { yaml } from '@codemirror/lang-yaml';

export { createDataView, createVarsView, createTemplateView };

const defaultExtensions = [
  history(),
  drawSelection(),
  highlightTrailingWhitespace(),
  highlightSelectionMatches(),
  indentUnit.of('  '),
  keymap.of([
    indentWithTab,
    ...defaultKeymap,
    ...historyKeymap
  ])
];

const replaceTabWithComma = ({ state, dispatch }) => {
  if (state.readOnly) {
    return false;

  } else {
    dispatch(state.update({
      changes: {
        from: state.selection.main.head,
        insert: ', '
      },
      selection: {
        anchor: state.selection.main.head + 2
      },
      scrollIntoView: true
    }));
    return true;
  }
};

function createDataView(_parent) {
  return new EditorView({
    parent: _parent,
    extensions: [
      keymap.of([
        { key: 'Tab', run: replaceTabWithComma }
      ])
    ].concat(defaultExtensions)
  });
}

function createVarsView(_parent) {
  return new EditorView({
    parent: _parent,
    extensions: [
      yaml(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true })
    ].concat(defaultExtensions)
  });
}

function createTemplateView(_parent) {
  return new EditorView({
    parent: _parent,
    extensions: [
      highlightActiveLineGutter(),
      lineNumbers()
    ].concat(defaultExtensions)
  });
}
