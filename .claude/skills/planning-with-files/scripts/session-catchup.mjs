#!/usr/bin/env node
/*
 * Session Catchup Script for planning-with-files
 *
 * Analyzes the previous session to find unsynced context after the last
 * planning file update. Designed to run on SessionStart.
 *
 * Usage: node session-catchup.mjs [project-path]
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const PLANNING_FILES = ["task_plan.md", "progress.md", "findings.md"];
const PATH_SEPARATOR_REGEX = /\//g;
const UNDERSCORE_REGEX = /_/g;

function homeDir() {
	if (process.platform === "win32") {
		return process.env.USERPROFILE || os.homedir();
	}
	return process.env.HOME || os.homedir();
}

function getProjectDir(projectPath) {
	let sanitized = projectPath.replace(PATH_SEPARATOR_REGEX, "-");
	if (!sanitized.startsWith("-")) {
		sanitized = `-${sanitized}`;
	}
	sanitized = sanitized.replace(UNDERSCORE_REGEX, "-");
	return path.join(homeDir(), ".claude", "projects", sanitized);
}

function getSessionsSorted(projectDir) {
	return fs
		.readdirSync(projectDir)
		.filter((fileName) => fileName.endsWith(".jsonl") && !fileName.startsWith("agent-"))
		.map((fileName) => {
			const filePath = path.join(projectDir, fileName);
			return {
				filePath,
				mtimeMs: fs.statSync(filePath).mtimeMs,
			};
		})
		.toSorted((a, b) => b.mtimeMs - a.mtimeMs)
		.map((session) => session.filePath);
}

function parseSessionMessages(sessionFile) {
	const messages = [];
	const lines = fs.readFileSync(sessionFile, "utf8").split("\n");

	lines.forEach((line, lineNum) => {
		try {
			const data = JSON.parse(line);
			data._line_num = lineNum;
			messages.push(data);
		} catch {
			// Match the Python implementation: invalid JSONL rows are ignored.
		}
	});

	return messages;
}

function findLastPlanningUpdate(messages) {
	let lastUpdateLine = -1;
	let lastUpdateFile = null;

	for (const msg of messages) {
		if (msg.type !== "assistant") {
			continue;
		}

		const content = msg.message?.content ?? [];
		if (!Array.isArray(content)) {
			continue;
		}

		for (const item of content) {
			if (item?.type !== "tool_use") {
				continue;
			}

			const toolName = item.name ?? "";
			const toolInput = item.input ?? {};

			if (toolName === "Write" || toolName === "Edit") {
				const filePath = toolInput.file_path ?? "";
				for (const planningFile of PLANNING_FILES) {
					if (filePath.endsWith(planningFile)) {
						lastUpdateLine = msg._line_num;
						lastUpdateFile = planningFile;
					}
				}
			}
		}
	}

	return [lastUpdateLine, lastUpdateFile];
}

function extractMessagesAfter(messages, afterLine) {
	const result = [];

	for (const msg of messages) {
		if (msg._line_num <= afterLine) {
			continue;
		}

		const msgType = msg.type;
		const isMeta = msg.isMeta ?? false;

		if (msgType === "user" && !isMeta) {
			let content = msg.message?.content ?? "";

			if (Array.isArray(content)) {
				const textItem = content.find((item) => item && item.type === "text");
				content = textItem?.text ?? "";
			}

			if (content && typeof content === "string") {
				if (
					content.startsWith("<local-command") ||
					content.startsWith("<command-") ||
					content.startsWith("<task-notification")
				) {
					continue;
				}

				if (content.length > 20) {
					result.push({ role: "user", content, line: msg._line_num });
				}
			}
		} else if (msgType === "assistant") {
			const msgContent = msg.message?.content ?? "";
			let textContent = "";
			const toolUses = [];

			if (typeof msgContent === "string") {
				textContent = msgContent;
			} else if (Array.isArray(msgContent)) {
				for (const item of msgContent) {
					if (item?.type === "text") {
						textContent = item.text ?? "";
					} else if (item?.type === "tool_use") {
						const toolName = item.name ?? "";
						const toolInput = item.input ?? {};

						if (toolName === "Edit") {
							toolUses.push(`Edit: ${toolInput.file_path ?? "unknown"}`);
						} else if (toolName === "Write") {
							toolUses.push(`Write: ${toolInput.file_path ?? "unknown"}`);
						} else if (toolName === "Bash") {
							const command = (toolInput.command ?? "").slice(0, 80);
							toolUses.push(`Bash: ${command}`);
						} else {
							toolUses.push(toolName);
						}
					}
				}
			}

			if (textContent || toolUses.length > 0) {
				result.push({
					role: "assistant",
					content: textContent ? textContent.slice(0, 600) : "",
					tools: toolUses,
					line: msg._line_num,
				});
			}
		}
	}

	return result;
}

function main() {
	const projectPath = process.argv[2] || process.cwd();
	const projectDir = getProjectDir(projectPath);

	const hasPlanningFiles = PLANNING_FILES.some((fileName) =>
		fs.existsSync(path.join(projectPath, fileName)),
	);
	if (!hasPlanningFiles) {
		return;
	}

	if (!fs.existsSync(projectDir)) {
		return;
	}

	const sessions = getSessionsSorted(projectDir);
	if (sessions.length < 1) {
		return;
	}

	let targetSession = null;
	for (const session of sessions) {
		if (fs.statSync(session).size > 5000) {
			targetSession = session;
			break;
		}
	}

	if (!targetSession) {
		return;
	}

	const messages = parseSessionMessages(targetSession);
	const [lastUpdateLine, lastUpdateFile] = findLastPlanningUpdate(messages);

	if (lastUpdateLine < 0) {
		return;
	}

	const messagesAfter = extractMessagesAfter(messages, lastUpdateLine);
	if (messagesAfter.length === 0) {
		return;
	}

	console.log("\n[planning-with-files] SESSION CATCHUP DETECTED");
	console.log(`Previous session: ${path.basename(targetSession, path.extname(targetSession))}`);
	console.log(`Last planning update: ${lastUpdateFile} at message #${lastUpdateLine}`);
	console.log(`Unsynced messages: ${messagesAfter.length}`);

	console.log("\n--- UNSYNCED CONTEXT ---");
	for (const msg of messagesAfter.slice(-15)) {
		if (msg.role === "user") {
			console.log(`USER: ${msg.content.slice(0, 300)}`);
		} else {
			if (msg.content) {
				console.log(`CLAUDE: ${msg.content.slice(0, 300)}`);
			}
			if (msg.tools?.length) {
				console.log(`  Tools: ${msg.tools.slice(0, 4).join(", ")}`);
			}
		}
	}

	console.log("\n--- RECOMMENDED ---");
	console.log("1. Run: git diff --stat");
	console.log("2. Read: task_plan.md, progress.md, findings.md");
	console.log("3. Update planning files based on above context");
	console.log("4. Continue with task");
}

main();
