### CodeMirror 6 Editor Build

```
npm install rollup terser codemirror

npm install @rollup/plugin-node-resolve

npm install @codemirror/view
npm install @codemirror/language
npm install @codemirror/commands
npm install @codemirror/search
npm install @codemirror/lang-yaml
```

```
npx rollup editor.mjs -f iife -o cm6.bundle.js -p @rollup/plugin-node-resolve --output.name cm6

npx terser cm6.bundle.js -c -m --output ../../jinjafx_server/www/js/cm6.bundle.min.js
```
