// Geometry-safe svgo settings for the official logos: strip editor metadata and unused ids,
// never touch path data, numbers, transforms or shapes. tests/test_logos.py proves it.
export default {
  multipass: false,
  js2svg: { pretty: false, eol: 'lf', finalNewline: true },
  plugins: [
    'removeDoctype',
    'removeXMLProcInst',
    'removeComments',
    'removeMetadata',
    'removeEditorsNSData',
    'cleanupAttrs',
    'removeEmptyAttrs',
    'removeEmptyText',
    'removeEmptyContainers',
    { name: 'removeAttrs', params: { attrs: ['data-figma-.*'] } },
    { name: 'cleanupIds', params: { minify: true, remove: true } },
  ],
};
