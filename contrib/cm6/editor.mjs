import { basicSetup, EditorView } from 'codemirror';
export { createEditorView };

function createEditorView(_parent) {
  return new EditorView({
    parent: _parent,
    extensions: [basicSetup]
  });
}
