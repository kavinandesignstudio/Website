# Going live: GitHub Pages + Zoho Domains

*Free hosting with free HTTPS on GitHub, using your domain from Zoho. About 1 hour of clicking,
plus up to a day for the domain to connect.*

**What you'll end up with**

- `https://www.kavinandesignstudio.com` served by GitHub Pages. `kavinandesignstudio.com` (without www) redirects to it.
- Every edit you push goes live in about 2 minutes.
- Every morning at 06:00 IST the site rebuilds by itself. That publishes scheduled journal posts, plus
  AI-written posts and FAQs from your notes in `content/updates/` if you add an Anthropic key.
- Contact and AI Platform forms email you through Web3Forms (free).
- **Your Zoho email (`ar.srk@kavinandesignstudio.com`) keeps working.** We only add website records.

---

## Step 1: Create the GitHub account and repository (15 min)

1. Sign up at **github.com** with the studio email. Choose a short username, e.g. `kavinandesignstudio`.
   Below, `USERNAME` means this username.
2. Install **GitHub Desktop** from **desktop.github.com** and sign in with that account.
3. In GitHub Desktop: **File → Add local repository…** → choose `D:\KDS\website`.
   It says *"This directory does not appear to be a Git repository"* → click **create a repository**.
   - Name: **`USERNAME.github.io`** (exactly your username + `.github.io`; recommended, see note below)
   - Leave *Git ignore* and *License* as **None** (the package already has a `.gitignore`)
   - Click **Create repository**.
4. Click **Publish repository**.
   - **Untick "Keep this code private".** GitHub Pages is free only for public repositories.
     A private repository needs GitHub Pro, which is paid.
   - Public is safe here: the repository contains only website text, images and code.
     Your API key goes into GitHub *Secrets*, which nobody can see.

> **Why the repository name `USERNAME.github.io`?** With that name the site also works at
> `https://USERNAME.github.io/` while you wait for the domain. With any other name, the temporary
> address has an extra folder (`…github.io/kavinan-website/`). The site then *looks broken* (no styling)
> until your own domain is connected. Once the domain works, both names behave the same.

## Step 2: Switch on GitHub Pages (5 min)

1. On github.com open your repository → **Settings → Pages**.
2. Under **Build and deployment → Source** choose **GitHub Actions**.
3. Open the **Actions** tab → if asked, click **I understand my workflows, go ahead and enable them**.
4. Click **Build & publish website** → **Run workflow** → **Run workflow**.
5. After about 2 minutes you'll see a green tick. Visit `https://USERNAME.github.io/` and your site is live.

## Step 3: Point your Zoho domain to GitHub (15 min + waiting)

### 3a. Tell GitHub about the domain
Repository → **Settings → Pages → Custom domain** → type `www.kavinandesignstudio.com` → **Save**.
It will say the DNS check is in progress. That's expected until 3c is done.

### 3b. Verify the domain with GitHub (recommended, protects it from misuse)
1. Click your profile photo (top right) → **Settings → Pages** (in the left menu, under *Code, planning and automation*) → **Add a domain**.
2. Enter `kavinandesignstudio.com`. GitHub shows a **TXT record** like
   `_github-pages-challenge-USERNAME` with a value. Keep this page open.

### 3c. Add the records in Zoho Domains
1. Sign in at **domains.zoho.com** (or Zoho Domains from your Zoho account).
2. Open **kavinandesignstudio.com → DNS Management** (sometimes called *Manage DNS*).
3. **Remove** any existing **A** record for `@` and **CNAME** for `www` that point somewhere else
   (parking page, old host). Switch off any *URL forwarding / redirect* set on the domain.
4. **Do not touch** records used by your email: **MX**, **TXT** containing `v=spf1`, **DKIM**
   (`…._domainkey`), or `zoho-verification` / `zb…` records.
5. **Add** these records:

| Type | Host / Name | Value / Points to | TTL |
|---|---|---|---|
| A | `@` | `185.199.108.153` | default |
| A | `@` | `185.199.109.153` | default |
| A | `@` | `185.199.110.153` | default |
| A | `@` | `185.199.111.153` | default |
| AAAA *(optional)* | `@` | `2606:50c0:8000::153` | default |
| AAAA *(optional)* | `@` | `2606:50c0:8001::153` | default |
| AAAA *(optional)* | `@` | `2606:50c0:8002::153` | default |
| AAAA *(optional)* | `@` | `2606:50c0:8003::153` | default |
| CNAME | `www` | `USERNAME.github.io` | default |
| TXT | `_github-pages-challenge-USERNAME` | *(the value GitHub showed in 3b)* | default |

   In Zoho, `@` may be shown as the bare domain or left blank. Use whatever Zoho uses for the "root" domain.

6. Save. DNS usually updates in 15–60 minutes and can take up to 24 hours.
   You can watch progress at **dnschecker.org** (search `www.kavinandesignstudio.com`, type CNAME).

### 3d. Finish in GitHub
1. Back in **profile Settings → Pages**, click **Verify** next to your domain.
2. Repository → **Settings → Pages**: when it shows *"DNS check successful"*, tick **Enforce HTTPS**.
   The free certificate can take up to an hour. If the box is greyed out, wait and refresh.
3. Open **https://www.kavinandesignstudio.com** and the site is live. 🎉

## Step 4: Make the forms deliver to your inbox (5 min)

GitHub Pages can't receive form submissions, so the site uses **Web3Forms** (free, 250 submissions a month).

1. Go to **web3forms.com** → enter `kavinandesignstudio@gmail.com` → **Create Access Key**.
2. Copy the key from the email you receive.
3. Open `content/site.json`, find the `"form"` section, and paste the key between the quotes after `"access_key":`.
4. Save, then in GitHub Desktop write a short summary (e.g. *Add form key*) → **Commit to main** → **Push origin**.
5. After about 2 minutes, send a test enquiry from the Contact page. Check the spam folder the first time
   and mark it *Not spam*.

Until the key is added, the forms open the visitor's email app with their details filled in.
No enquiry is lost.

## Step 5: Switch on automatic articles (optional, 5 min)

Scheduled posts already go live every morning without this step.
To have Claude also write articles and FAQs from your notes in `content/updates/`:

1. Create an API key at **console.anthropic.com** (add a small amount of credit; each article costs only a few rupees).
2. Repository → **Settings → Secrets and variables → Actions → New repository secret**
   → Name `ANTHROPIC_API_KEY`, paste the key → **Add secret**.
3. Optional: **Variables** tab → `AUTO_PUBLISH` = `false` if you want to approve each AI post first.
   New posts then arrive with `draft: true`; change it to `false` to publish.

> GitHub pauses scheduled workflows on public repositories after **60 days without any commits**.
> If you get an email about this, open the **Actions** tab and click **Enable workflow**. Adding an
> update note now and then also keeps it active.

---

## Everyday editing

| You want to… | Do this |
|---|---|
| Change text, add a post, FAQ or project | Edit files in `D:\KDS\website\content\` → GitHub Desktop → **Commit to main** → **Push origin**. Live in ~2 min. |
| Quick fix from any computer | On github.com open the file → ✏️ pencil icon → edit → **Commit changes**. |
| Add new photos | Run `python tools/optimize_images.py` on your PC first (see README), then commit & push. |
| See if publishing worked | **Actions** tab: green tick = live, red cross = click it to see which file has a mistake. |

## Troubleshooting

| Problem | Fix |
|---|---|
| Site looks unstyled at `USERNAME.github.io/something/` | The repository isn't named `USERNAME.github.io`. Use your custom domain, or rename the repository (Settings → General). |
| "Domain does not resolve to the GitHub Pages server" | DNS still updating, or an old A/CNAME record is still in Zoho. Re-check step 3c. |
| Enforce HTTPS is greyed out | Wait up to an hour after DNS succeeds, then refresh. |
| Custom domain disappears from settings | Re-enter `www.kavinandesignstudio.com` in Settings → Pages. The site's `CNAME` file also keeps it set. |
| Workflow shows a red cross | Open it. Usually a typo in a `.json` file (a missing comma or quote). The error names the file and line. |
| Email stopped working | An MX/TXT email record was removed in Zoho. Restore them from Zoho Mail → Domains → DNS mapping. |
| Form says it couldn't send | Access key missing or wrong in `content/site.json` (Step 4). |
