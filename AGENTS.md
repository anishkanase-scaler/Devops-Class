# DevOps & Cloud [SWE] — Course Notes Repo

This repo holds raw lecture transcripts and structured notes for a DevOps & Cloud course (Scaler Academy), one folder per class.

⚠️ **Folder naming is inconsistent** — Classes 1–8 are bare (`Class-01`…`Class-08`); from 9 onward they carry the topic (`Class-09-Kubernetes Fundamentals`, `Class-13-Kubernetes Storage, HPA & Probes`). Names contain spaces, `&` and commas, so **always quote paths** in shell commands. Never rename a folder unprompted — the user reorganises this repo between sessions, so match whatever is on disk.

📅 **Class numbers are chronological by lecture date** (re-done on 4 Oct 2026 at the user's request: folders 14–21 were renumbered/renamed so each number matches its date and its name matches what was *actually taught*, and the working files were moved into the matching folder). New raw transcripts get dropped into `transcripts/` as `<Title>_-_Class_Scaler_Academy.txt` — read the header's `Start Time`, work out the next class number by date, verify the real topic from the text, then move it to `Class-NN-<Real Topic>/transcript`.

## Key facts about this course

- **The instructor is Nensi Ravaliya** — GitHub [@Nency-Ravaliya](https://github.com/Nency-Ravaliya), a **DevSecOps Engineer at Standard Chartered**, AWS Community Builder, Udemy/YouTube instructor. She's heard as *"Nancy"* in the ASR and writes `Nensi` in her own scripts.
- ⚠️ **"Ritesh Prajapati" in every transcript header is NOT the instructor** — that's the developer of the *Scaler++ Chrome extension* that downloaded the file. Never put that name in the `**Instructor:**` field.
- 🏠 **THE MAIN REPO OF THE INSTRUCTOR: [`https://github.com/Nency-Ravaliya/devops-heros`](https://github.com/Nency-Ravaliya/devops-heros)** — the "DevOps Heroes" repo she promised the batch in Class 2. One folder per session (`session1-…` → `session21-python`) with her own scripts, Dockerfiles, compose files, YAML, Helm charts, workflows, Terraform and PDFs. **This is a primary source, not a classmate's repo** — check it for every class, before writing notes, and treat it like the class's own working directory. A local clone sits at `../devops-heros` (it has local changes and has diverged from GitHub — don't pull into it; take a fresh `git clone --depth 1` into the scratchpad when you need the latest).
- **Her session folders ↔ our class folders** (her numbering drifts from ours — go by date and content):

| Our class | Date | Her repo folder |
|---|---|---|
| 14 | 17 Sep | `session-12-ingress-configmaps-secrets` |
| 15 | 21 Sep | `session-14-kubernetes-troubleshooting` |
| 16 | 22 Sep | `session-15-helm` |
| 17 | 24 Sep | `session-16-github-actions` |
| 18 | 25 Sep | `session-17-devsecops` |
| 19 | 29 Sep | `session18-terraform-iac` |
| 20 | 3 Oct | `session19-cloud-terraform` |
| — | *(no class recorded yet)* | `session20-monitoring-observability-gitops` |
| 21 | 4 Oct | `session21-python` (final project) |
- She maintains **satellite repos** linked from the session folders, e.g. [Networking](https://github.com/Nency-Ravaliya/Networking), [How-DHCP-Works](https://github.com/Nency-Ravaliya/How-DHCP-Works), [Subnetting](https://github.com/Nency-Ravaliya/Subnetting), [IP-quest](https://github.com/Nency-Ravaliya/IP-quest), [IPFIX-NETFLOW-NTP](https://github.com/Nency-Ravaliya/IPFIX-NETFLOW-NTP), [Kubernetes](https://github.com/Nency-Ravaliya/Kubernetes).
- **Coverage status** (re-verify with `ls` every session — it changes):

| Class | Topic | Transcript | Notes |
|---|---|---|---|
| 01–08 | DevOps intro → Docker volumes | ✅ | ✅ |
| 09 | Kubernetes Fundamentals | ✅ | ✅ |
| 10 | Pods, ReplicaSets & Deployments | ✅ | ✅ |
| **05** | Git & GitHub | ❌ **never recorded** | ❌ |
| 11 | Networking & Services | ✅ *(the earlier duplicate-of-Class-10 file was replaced 16 Sep — re-verify with `md5` if it ever looks off)* | ✅ |
| 12 | *(folder says Ingress/ConfigMaps/Secrets)* | ✅ | ✅ |
| 13 | *(folder says Storage/HPA/Probes)* | ✅ | ✅ |
| 14 | ConfigMaps, Secrets & Ingress *(folder renamed from `Class-14-Helm`)* | ✅ | ✅ |
| 15 | Kubernetes Troubleshooting (21 Sep) | ⚠️ **empty** — header "Kubernetes 8", only ~30 s of screen-share setup. Notes built from her `session-14-kubernetes-troubleshooting` folder, no quotes/quiz | ✅ |
| 16 | Helm (22 Sep) — title correct | ✅ | ✅ |
| 17 | CI/CD & GitHub Actions (24 Sep) — title correct; CI hands-on, CD theory only. `hey-cicd/` lives here | ✅ | ✅ |
| 18 | DevSecOps Pipeline & Four-Way Deployment (25 Sep) — header "Complete CI/CD & DevSecOps" | ✅ | ✅ |
| 19 | Terraform & Infrastructure as Code (29 Sep) — title correct | ✅ | ✅ |
| 20 | Cloud, VPC & Terraform (3 Oct) — header "Cloud & Terraform in Action" | ✅ | ✅ |
| 21 | Final DevOps Project Brief & Exam Prep (4 Oct) — header "Final Devops Project & Trouble Shooting_2" | ✅ | ✅ |

- ⚠️ **From Class 12 on, the lecture titles are often WRONG** (16, 17, 19 and 20 were right). The folder name and the transcript header both state the *planned* topic, not what was taught. **Always read the transcript before trusting the title.** Confirmed so far:
  - **Class 12** says *Ingress, ConfigMaps & Secrets* → actually **DaemonSets, rolling updates, rollout commands, deployment strategies**
  - **Class 13** says *Storage, HPA & Probes* → actually **the five Service types, StatefulSet vs Deployment, FQDN**
  - **Class 14** said *Helm* → actually **ConfigMaps, Secrets & Ingress** (Helm came in Class 16).
  - **Class 15** said *Kubernetes 8* → **Kubernetes troubleshooting** (from her repo; recording empty).
  - **Class 18** said *Complete CI/CD & DevSecOps* → roughly right, but ~70% was one Flask app deployed four ways (by hand → Docker/Docker Hub → Minikube → a 7-job GitHub Actions pipeline); the DevSecOps part (CodeQL, pip-audit, Trivy) was ~25 min. Secret scanning, GHCR and the `--exit-code` gate were *not* taught.
  - **Class 21** said *Final Devops Project & Trouble Shooting_2* → actually the **capstone brief** (TaskBoard project, 100-pt rubric, pipeline, deadlines) and **end-term exam pattern**; no troubleshooting beyond one live compose crash.
  - Storage, HPA and Probes were apparently covered in the uncaptured 21 Sep slot and drilled in Class 16's recap — there are no notes of their own for them. **Monitoring/Prometheus/Grafana/ArgoCD** (her `session20-…`) has no class transcript yet.
- 🔁 **She repeats topics across sessions on purpose — so the notes repeat them too.** Known repeats: the **Kubernetes architecture** (Classes 9, 10, 13), **`maxSurge`/`maxUnavailable`** and the **deployment strategies** (11, 12), **ReplicaSet vs Deployment** (11, 12, 13), **`create` vs `apply`** (10, 11, 13), **labels vs selectors** (11, 12, 13), **the four ports** (11, 13), **DaemonSet** (11, 12).
- **Her session numbering ≠ folder numbering.** She says "session 10 / session 11" for material in `Class-12`. Don't try to reconcile them; go by content (see the mapping table above).

## Layout convention

- `Class-NN/transcript` — raw, auto-generated transcript (via the "Scaler++ Chrome Extension"). Unedited and ASR-noisy. **Classes 1–6 used a poor transcriber** and are littered with stray Hindi/Telugu/Portuguese/Ukrainian/Spanish/Indonesian fragments. **From Class 7 onward the header shows `Model use: groq, whisper-large-v3-turbo`** and the quality is dramatically better.
- `Class-NN/notes.md` — the structured version. **This is the deliverable.**
- `Class-NN/notes.pdf` — generated, see the PDF pipeline below.
- `Class-NN/*.sh`, `*.yml`, `*.png`, `homework/`, working folders — the actual files the student wrote/ran in class. **These are ground truth** for exact commands, filenames and outputs — more reliable than the ASR, so always cross-check them.
- ⚠️ **Do NOT create `README.MD` files.** Each class already has the user's own README. The deliverable is **`notes.md` → `notes.pdf`**, nothing else.
- Screenshots live wherever they were saved (`Class-06/image.png`, `Class-06/exec.png`, `Class-06/dockerdf.png`, `Class-08/connectBackend.png`, `bindvolume.png` at repo root). **Read them with the `Read` tool and embed them in the relevant notes** with a markdown image and a short "what this proves" explanation.

---

## Task: turning a `transcript` into `notes.md`

When asked to "structure" a class transcript — or whenever a new `Class-NN/transcript` shows up without a matching `notes.md` — produce `Class-NN/notes.md` following the convention below. No need to re-ask for the format.

### The voice: simple, fun, never boring

This is the **defining constraint** of the format. The notes should read like a sharp friend explaining the class, not like a textbook.

1. **Short sentences. Plain words.** Prefer "one big box" over "a monolithic deployment artifact."
2. **Lead with an analogy, then the jargon** — never the other way round. The instructor does this constantly (rented flat vs own house, Zepto as a grocery registry, a Dockerfile as a tea recipe, the kitchen as the Docker daemon); keep hers, and add your own where a concept is bare.
3. **Keep the human moments.** Tech failures, jokes, her career stories, the applause when someone deploys their first container, students getting things wrong. They make the notes readable and they're part of what happened.
4. **Quote her.** Direct quotes in *italics* carry the personality — use them for definitions, punchlines and warnings.
5. **Use emoji as signposts**, not decoration — in section titles and callout labels (see below).
6. **Tables over paragraphs** for anything comparative. Fenced code blocks and ASCII diagrams for anything with a flow.

### Required structure

```markdown
# DevOps & Cloud [SWE] — Class N Notes

**Lecture Title:** <from transcript>
**Date/Time:** <from transcript, written out: "27 August 2026, 2:00 PM">
**Duration:** <from transcript>
**Instructor:** Nensi Ravaliya
**Big idea:** <one sentence — the single thing to remember>
**Sources:** <transcript + working files + repo links, when non-obvious>

---

## 0. The 60-Second Version

<6–8 numbered points. Someone who reads ONLY this should have the class.>

---

## 1. …
```

Then:

7. **Preserve everything the instructor covered.** Don't drop technical content, examples, numbers, command names, or the reasoning behind a concept. Reorganising and cleaning up phrasing is expected; silently dropping substance is not.
8. **Organise by topic, not chronologically-verbatim.** `##` for major sections (numbered from `0.`), `###` for sub-topics.
9. **Always include a logistics/warm-up section** — attendance, scheduling, resources shared, tech failures, banter. Brief, but don't omit it.
10. **Capture quiz / team-relay activity** as a table: question → who was asked → answer given → verdict (✅/❌).
11. **Cross-reference the class's working directory** — read the scripts, logs, YAML and screenshots and use them for exact commands and outputs.
12. **Review the student's own files.** Where their code has a bug or a wrong comment, say so kindly and explain the fix (see the `$(date)` quoting bug in Class 3 §11, the `image: heyyyy` typo in Class 10 §2). Where it's good, say why (the `0.0.0.0` bind in Class 6, the Apache `CMD` comment).
13. **Close with a cheat-sheet section** — every command and concept introduced, in tables grouped by category.
14. **Add a "Notes on the Transcript Itself" section** at the end: the instructor-name correction, transcription quality, which foreign-language stretches were folded in vs. unrecoverable, and a list of garbled-term corrections (`"demon" → daemon`, `"docker pool" → docker pull`, …).
15. **Handle non-English / garbled ASR fragments honestly.** Infer meaning from context and fold it into the relevant section. Pure noise (Norwegian subtitle credits, "thank you for watching", "like, share and subscribe") is skipped and mentioned once in §Transcript Notes.
16. **Don't fabricate outside content.** Stick to the transcript plus verified cross-references from the class's own files and her repos. Adding a standard reference table (private IP ranges, port numbers) where the audio garbled the numbers is fine — **label it** as filled in.
17. **Cover repeated material IN FULL every time — never defer to another class.** The user's explicit instruction: *"if instructor covers anything multiple times, you also cover it multiple times."* So if she re-teaches the architecture for the third time, write the third full explanation — don't write "see Class 9 §12". Vary the angle the way she does (a diagram one time, a Q&A drill the next, a worked example the third), and add a short `📌` note saying it's a deliberate repeat so the reader knows it's not an editing mistake.
    - ✅ **Connective cross-references are still good** — *"that's Docker's PID 1 rule again (Class 6 §13)"* links a concept to where it was first met without withholding anything. The test is: **would a reader who only has this one PDF be missing something?** If yes, write it out here.
    - Each `notes.pdf` must stand alone.
18. **Lead with practice.** The user's standing request: *"include many examples and practical things, and steps to practise myself."* So every hands-on topic gets a **numbered `🏋️` lab** the student can run start to finish, and every multi-step mechanism gets a **`🎬` frame-by-frame sequence** (a PDF can't animate — frames are the honest substitute; don't promise animation).
19. **Explain the terms she uses but never defines.** The transcripts are full of words dropped in passing — `OSI layers`, `three-tier`, `API`, `NAT`, `kernel`, `sudo`, `SSH key pair`, `cron`, `exit code`, `PV/PVC`, `headless service`. Where a learner would stall, add a short 🧠/💡 callout with **a diagram or a worked example**, not paragraphs. Keep them **few and relevant** — one per genuine gap, not one per noun. And **answer the homework she sets** (soft vs hard link, `journalctl`, `adduser` vs `useradd`) in a clearly-marked ✅ callout, so the notes work as a study reference after the student has tried it themselves.
20. **If the instructor's explanation is genuinely confusing, incomplete, or conflates two distinct things — clarify it, but as an ADDITION, never a silent rewrite.** Keep her version first (that's what's testable in her course), then add a `> 🔍 **Simplified/Clarified, since…**` callout with the more precise version, and say plainly which answer to give in *her* assessment. Established examples:
    - **init container vs sidecar** (Class 9 §15) — she calls them the same thing; they aren't.
    - **`--network host` on macOS** (Class 8 §10) — she says "your laptop's fault"; it's Docker Desktop's Linux VM.
    - **`curl` is not a Windows command** (Class 1 §7) — she rejects it; the real distinction is application-layer vs network-layer testing.
    - **`chmod +w -r`** (Class 3 §4) — the class says "not possible"; it is possible, just unwise.
    - **`depends_on` waits for *started*, not *ready*** (Class 9 §6).
    - **`containerd` was extracted from Docker**, not a replacement for it (Class 9 §14, Class 10 §5).
    - **A headless service IS reachable inside the cluster** (Class 13 §8) — she says it isn't. This is the biggest one; `clusterIP: None` means "no single virtual IP", not "no access".
    - **A revision is created when the pod template changes**, not on every `apply` (Class 12 §5).
    - **`--network host` / `minikube ip` failing on macOS** is Docker Desktop's Linux VM, not "a Mac issue" — the fix is `minikube service <name> --url` (Class 13 §5).
    Don't reach for this on ordinary ASR garbling or casual imprecision — only where a learner would walk away with a wrong mental model.
21. **If the user points to a classmate's/reference GitHub repo**, treat it like the class's own working directory: fetch it (`gh api repos/<owner>/<repo>/contents/<path>`, or just `git clone --depth 1` into the scratchpad — `gh` is authenticated here) and use it to fill gaps the transcript doesn't capture. Attribute it clearly per section plus a line in **Sources**.

### The callout system

Emoji-led blockquotes render as colour-coded cards in the PDF. **Use these exact emoji** — the renderer keys off them:

| Write | Renders as | Use for |
|---|---|---|
| `> 🧠 **…**` | violet — *Picture this* | analogies, mental models |
| `> 💡 **…**` | amber — *Good to know* | useful side facts, tips |
| `> ⚠️ **…**` | red — *Watch out* | gotchas, dangerous commands |
| `> ✅ **…**` | green — *Lock this in* | the thing to remember |
| `> 🎯 **…**` | pink — *Interview alert* | interview/exam questions |
| `> 🎤 **…**` | slate — *Said in class* | direct quotes |
| `> 🔍 **…**` | teal — *Clarified* | rule 17 corrections |
| `> 😄 **…**` | blue — *Class moment* | jokes, live failures, banter |
| `> 🔥 **…**` | orange — *Hard mode* | the hardest material / big stories |
| `> 📌 **…**` | blue — *Note* | sourcing notes, small asides |
| `> 🧪 **…**` | teal — *Try it yourself* | hands-on exercises |
| `> 🎬 **…**` | indigo — *Watch it happen* | frame-by-frame step sequences (the closest a PDF gets to an animation) |
| `> 🏋️ **…**` | teal — *Do this yourself* | numbered lab steps the student runs |
| `> 🧩 **…**` | violet — *Why it works* | the mechanism behind something she only asserted |
| `> 📝 **…**` | — | homework/assignments |

**Callouts can hold anything** — fenced code blocks, ASCII diagrams and tables all render properly inside them, which is where most of the explainer diagrams live:

```markdown
> 🧠 **What a layer physically is.**
>
> ```
> FROM ubuntu:24        →  layer 1
> RUN apt install node  →  layer 2
> ```
>
> | Tag | Size |
> |---|---|
> | `node:24` | ~1.1 GB |
```

(The renderer handles this by pulling each blockquote out and converting its inner markdown separately — see the pipeline notes below. You don't need blank `>` separator lines.)

---

## Task: turning `notes.md` into a PDF

There's a reusable pipeline — don't re-derive it.

```bash
.venv/bin/python scripts/notes_to_pdf.py Class-NN/notes.md Class-NN/notes.pdf
```

**What the script produces:**

- **A per-class colour theme**, auto-picked from the `Class-NN` folder name (`THEMES` dict at the top — 1 Sunrise · 2 Deep Ocean · 3 Terminal Green · 4 Grape Soda · 6 Docker Whale · 7 Neon Nights · 8 High Voltage · 9 Compose Teal · 10 Kube Indigo · 11 Lagoon · 12 Ember · 13 Signal Blue · 14 Moss · 15 Magma · 16 Iris. **Add a new entry when a new class appears**, otherwise it falls back to grey Graphite.). Theme drives the cover gradient, table headers, rules and footer.
- **A dark gradient cover page** — metadata card + a two-column "what's inside" chip grid with per-section numbers, emoji and accent colours.
- **Rainbow section headers** — every `##` gets its own accent from a rotating 9-colour cycle (`SECTION_ACCENTS`), a numeral badge, and an emoji.
- **Colour-coded callout cards** from the emoji blockquotes above.
- **Terminal-styled code blocks** (Pygments `dracula`, traffic-light dots).
- **Zebra tables**, `- [x]` tick lists, page numbers, running footer.

⚠️ **Never put a callout inside the metadata header block** (above the first `---`) — it renders inside the dark cover card. Put "read this first" warnings in the **body**, just after the `---` and before `## 0.`. (There is now a CSS guard so text stays legible if it happens, but the layout still looks wrong.)

**Section emoji** come from `SECTION_EMOJI` (keyword → emoji). **You can also just put an emoji directly in the heading** — `## 12. 💎 The Bulk-Stop Command` — and it wins over the keyword map. Extend `SECTION_EMOJI` when a new class introduces a title the map doesn't cover.

**Environment:** the venv (`.venv/`, gitignored) has `weasyprint`, `markdown`, `pygments`, `pypdf`. WeasyPrint needs native `pango` + `gdk-pixbuf` (`brew install pango gdk-pixbuf`, already installed) and `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`, which the script sets itself via `os.environ` before importing weasyprint.

**Sanity-checking a PDF:** use the `Read` tool directly on the `.pdf` with a `pages` range — it renders pages as images. Always check page 1 (the cover) and a couple of body pages after any CSS change.

**How callouts are rendered (important if you touch the script):** python-markdown's fenced-code handler is a *preprocessor* that only sees ``` fences at the start of a line, so a fence behind a `> ` prefix never becomes a code block. `extract_blockquotes()` therefore lifts every top-level blockquote out, replaces it with a placeholder paragraph, renders the inner markdown with a fresh `Markdown` instance, and splices it back as a `<blockquote>`. The placeholder is padded with blank lines so a neighbouring list or paragraph can't swallow it, `restore_blockquotes()` has a loose fallback pass, and it **asserts** no placeholder survives — so a lost callout fails the build loudly instead of silently vanishing.

**Known rendering pitfalls already fixed** — don't reintroduce them:
- Empty markdown table headers (`| | |`) rendered as a blank coloured bar → the script now strips empty `<thead>` and styles the table as `.nohead`.
- The running footer bled onto the cover → `@page :first` blanks all three margin boxes.
- The cover's radial glow painted over the title → cover children need `position: relative`.
- Dark `em`/`code` text was invisible on the dark cover → `.cover em|code|strong|a` have their own colours.
- A numbered heading (`## 12. 💎 Title`) hid an explicit emoji → `pick_emoji` strips a leading `N. ` before testing.
- Code fences inside callouts silently degraded to wrapped inline code, and adjacent callouts merged into one card → both fixed by `extract_blockquotes()` above.
- A placeholder landing next to a list was absorbed as a lazy continuation line and the whole callout disappeared → placeholders are now blank-line padded, and the restore step asserts.
- A callout placed in the metadata header rendered white-bold-on-white inside the cover card → `.cover .callout` now restores dark text, but keep warnings in the body anyway.

---

## Task: `Class-NN/pre-class.md` — priming before a class happens

Separate from the post-class `notes.md` flow: when the user pastes an upcoming syllabus/topic list and asks for a pre-class primer, create `Class-NN/pre-class.md` covering just those topics. Rules deliberately different from `notes.md`:

1. **Simple over complete.** This runs *before* the class — the goal is walking in comfortable, not a reference doc. Cut anything genuinely advanced (deep protocol internals, maths, edge cases) unless asked for more depth.
2. **One plain-language analogy per concept**, introduced before any jargon — an IP address as a street address, a port as which door, DNS as a phonebook.
3. **Short sections**, one per topic, in the order given. Close with a one-line "quick recap" table mapping each term to its meaning.
4. **No metadata header block** (there's no lecture yet to cite) — just a title, the topic list, and a one-line framing sentence.
