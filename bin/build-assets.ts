#!/usr/bin/env node

// Build script to compile puzzle and round scripts/styles, plus some rewriting
// to use the built scripts/styles.

import * as fs from "fs";
import concurrently from "concurrently";
import * as chokidar from "chokidar";
import { Command } from "commander";
import { platform } from "os";
import { join, resolve, sep, posix, relative } from "path";
import { spawn, spawnSync } from "child_process";
import { build } from "esbuild";
import { uniqBy } from 'lodash';

const program = new Command();
program.option("-w, --watch", "Watch for changes");
program.parse();

const { watch } = program.opts();
const debug = !process.env.DJANGO_ENV || !process.env.DJANGO_ENV.startsWith('prod_');

const huntDirectory = resolve(__dirname, "../hunt");
const huntDataDirectory = join(huntDirectory, "data");
const npxCmd = platform().startsWith("win") ? "npx.cmd" : "npx";
const npmCmd = platform().startsWith("win") ? "npm.cmd" : "npm";

const RE_GEN_TAG = /\{\{gen:([a-z\-]*)\}\}/gi;

function runCommand(command: string, args: string[]) {
  spawn(command, args, {
    env: process.env,
    stdio: "inherit",
  });
}

function getCommandOutput(command: string, args: string[]): Promise<string> {
  console.debug(`     running command ${command} ${args.join(' ')}`);
  const handle = spawn(command, args, {
    env: process.env,
    stdio: ["ignore", "pipe", "inherit"],
  });
  const buffer: string[] = [];
  let resolve: (result: string) => void;
  const promise = new Promise<string>((innerResolve, innerReject) => {
    resolve = innerResolve;
  });
  handle.stdout.on('data', data => {
    buffer.push(data.toString('utf-8'));
  });
  handle.on('exit', data => {
    resolve(buffer.join(''));
  });
  return promise;
}

function assert(value: unknown, message: string): asserts value {
  if (!value) {
    throw Error(`Assertion errror: ${message}`);
  }
}

function maybeRemove(path: string) {
  console.debug(`Removing files from ${path}`);
  return new Promise((resolve, reject) => {
    fs.rm(path, { recursive: true, force: true }, (err) => {
      if (err) reject(err);
      else resolve(undefined);
    });
  });
}

// TODO(sahil): We can parallelize some work. And this is pretty brittle but works for now.
// TODO(sahil): We should watch for added files? A glob plugin may work well?

async function main() {
  const commands: concurrently.CommandObj[] = [];

  // Step 1: Find build targets.
  const scssTargets = [];
  const tsTargets = [];
  const htmlTargets = new Map<string, string>();

  for (const assetType of ["puzzle", "round"]) {
    const subPaths = ["./", "solution/"];
    if (assetType === "puzzle") {
      subPaths.push("posthunt/");
    }

    for (const slug of fs.readdirSync(join(huntDataDirectory, assetType))) {
      const path = join(huntDataDirectory, assetType, slug);
      if (!fs.statSync(path).isDirectory()) {
        continue;
      }

      for (const subPath of subPaths) {
        const fullPath = join(path, subPath, "style.scss");
        if (!fs.existsSync(fullPath)) continue;

        const outputFile = "style.compiled.css";
        scssTargets.push(`${fullPath}:${join(path, subPath, outputFile)}`);
        console.log(`Processing SCSS file: ${fullPath}`);
      }

      for (const subPath of subPaths) {
        // Only support TS for puzzles for now.
        if (assetType !== "puzzle") continue;

        const fullPath = join(path, subPath, "main.ts");
        if (!fs.existsSync(fullPath)) continue;

        const outputFile = "style.compiled.css";
        tsTargets.push(fullPath);
        console.log(`Processing TS file: ${fullPath}`);

        if (fs.existsSync(join(path, subPath, "index.template.html"))) {
          htmlTargets.set(fullPath, join(path, subPath));
        } else {
          console.warn(`No reference to TS file: ${fullPath}`);
        }
      }
    }
  }

  // Step 2: Build SCSS files.
  const scssArgs = [];
  if (watch) {
    scssArgs.push("--watch");
  }
  if (debug) {
    scssArgs.push("--embed-source-map");
    scssArgs.push("--embed-sources");
  } else {
    scssArgs.push("--style=compressed");
    scssArgs.push("--no-error-css");
    scssArgs.push("--no-source-map");
  }

  if (scssTargets.length) {
    commands.push({
      name: "sass",
      command: ["sass", ...scssArgs, ...scssTargets].join(" "),
      prefixColor: "blue",
      env: process.env,
    });
  }

  // Step 3: Build TS files and update HTML files to refer to them.
  let buildUpToDate = false;
  const {
    warnings,
    errors,
    metafile,
    rebuild: rebuildTs,
  } = await build({
    entryPoints: tsTargets,
    bundle: true,
    // Note: chunks are placed outside the puzzle directory because of how
    // esbuild works. We need to do some awkwardness to make references to them
    // work reliably.
    //  1) When in debug mode, we serve chunks from /chunks/ and have a
    //     view to handle them.
    //  2) When in non-debug mode, we rewrite JS files to fetch chunks from
    //     /static/chunks, and ensure they get deployed with static content.
    //     The rewriting is part of the deploy script.
    // Both are a little brittle but seem to work.
    splitting: true,
    format: "esm",
    sourcemap: debug ? "inline" : false,
    minify: !debug,
    watch,
    incremental: watch,
    entryNames: "[dir]/dist/[name]-[hash]",
    chunkNames: "chunks/[name]-[hash]",
    outbase: huntDataDirectory,
    outdir: huntDataDirectory,
    publicPath: "/",
    metafile: true,
    plugins: [
      {
        name: "compile-html",
        setup(build) {
          build.onStart(async () => {
            console.debug(`Starting build`);
            buildUpToDate = true;

            const promises = [];
            promises.push(maybeRemove(join(huntDataDirectory, "chunks")));
            for (const targetPath of htmlTargets.values()) {
              promises.push(maybeRemove(join(targetPath, "dist")));
              promises.push(maybeRemove(join(targetPath, "index.compiled.html")));
            }
            await Promise.all(promises);
          });
          build.onEnd(async (result) => {
            // TODO(sahil): If building just index.template.html, we won't have
            // a metafile.
            const metafile = result.metafile;
            assert(metafile, "missing metafile");

            const mapping = new Map<string, string>();
            for (const hashedFilePath of Object.keys(metafile.outputs)) {
              const entryPoint = metafile.outputs[hashedFilePath].entryPoint;
              if (!entryPoint) continue;
              console.debug(`Finished TS build: ${entryPoint}`);

              rebuildHtml(hashedFilePath, entryPoint);
            }
          });
        },
      },
    ],
  });
  for (const warning of warnings) {
    console.warn(warning.text, warning);
  }
  for (const error of errors) {
    console.error(error.text, error);
  }

  async function rebuildHtml(hashedFilePath: string, entryPoint: string) {
    const htmlTargetPath = htmlTargets.get(
      resolve(process.cwd(), entryPoint)
    );
    if (!htmlTargetPath) return;

    const hashedFileRelativePath = hashedFilePath.slice(
      hashedFilePath.lastIndexOf("dist")
    );
    const templateHtml = await new Promise<string>((resolve, reject) => {
      fs.readFile(
        join(htmlTargetPath, "index.template.html"),
        { encoding: "utf-8" },
        (err, data) => {
          if (err) reject(err);
          else resolve(data);
        }
      );
    });
    console.debug(`Building HTML file: ${htmlTargetPath}`);

    const genTags = uniqBy(Array.from(templateHtml.matchAll(RE_GEN_TAG)), (matches) => matches[1]);
    const generatedBuilds = await Promise.all(genTags.map(async ([tag, scriptName]) => [
      tag,
      await getCommandOutput(npmCmd, [
        "run",
        "--silent",
        "ts:hunt",
        join(htmlTargetPath, "__build", `${scriptName}.ts`),
      ]),
    ]));
    console.debug(`Built HTML file: ${htmlTargetPath} (${generatedBuilds.length} deps)`);

    const compiledHtml = templateHtml
      .replace('src="main.ts', `src="${hashedFileRelativePath}`)
      .replace("src='main.ts", `src='${hashedFileRelativePath}`)
      .replace(
        RE_GEN_TAG,
        (genTag) =>
          generatedBuilds.find((build) => build[0] === genTag)![1]
      );
    await new Promise((resolve, reject) => {
      fs.writeFile(
        join(htmlTargetPath, "index.compiled.html"),
        compiledHtml,
        { encoding: "utf-8" },
        (err) => {
          if (err) reject(err);
          else resolve(undefined);
        }
      );
    });
    console.debug(`Written HTML file: ${htmlTargetPath}`);
  }

  if (watch) {
    // Add a watcher for index.template.html and __build.
    const chokidarPath = huntDataDirectory.replace(sep, posix.sep);
    chokidar
      .watch([
        `${chokidarPath}/**/index.template.html`,
      ], {
        ignoreInitial: true,
      })
      .on("all", (event, path) => {
        if (buildUpToDate) {
          console.debug(`chokidar triggering rebuild: ${event}`);
          rebuildTs();
          buildUpToDate = false;
        }
      });
  }

  // Step 4: Run TS type-checking.
  const watchArg = watch ? ["--watch"] : [];
  commands.push({
    name: "tsc",
    command: [
      "tsc",
      ...watchArg,
      `--project ${huntDirectory}`,
      "--noEmit",
      "--preserveWatchOutput",
    ].join(" "),
    prefixColor: "green",
    env: process.env,
  });

  concurrently(commands);
}

main();
