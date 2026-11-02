import tsParser from "@typescript-eslint/parser";

export default [{
  files: ["**/*.js", "**/*.mjs", "**/*.ts"],
  languageOptions: { parser: tsParser, ecmaVersion: "latest", sourceType: "module" },
  rules: {
    complexity: ["error", 10],
    "max-lines-per-function": ["error", { max: 60, skipBlankLines: true, skipComments: true }],
    "max-depth": ["error", 4],
    "max-classes-per-file": ["error", 1],
  },
}];
