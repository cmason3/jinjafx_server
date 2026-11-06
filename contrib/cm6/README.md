### CodeMirror 6 Editor Build

```
npm install rollup codemirror
npm install @rollup/plugin-node-resolve
```

```
npx rollup editor.mjs -f iife -o ../../jinjafx_server/www/js/cm6.bundle.js -p @rollup/plugin-node-resolve --output.name cm6
```
