#!/usr/bin/env bash
# GENERATED FILE. Canonical source: algominds-ai/algominds-standards
# -> greptile/greptile-budget.sh. Edit there, then run greptile/sync-greptile.sh.
#
# How much Greptile did we spend, measured from the GitHub side.
#
#   bash scripts/greptile-budget.sh              # since the 1st of this month
#   bash scripts/greptile-budget.sh 2026-07-25   # since a date
#
# Counts PRs that received at least one Greptile review. That is a LOWER BOUND on
# credits: a PR re-reviewed three times shows up once here but is billed three times.
# Treat the number as a floor, not a total. Needs `gh` authenticated.

set -uo pipefail
command -v gh >/dev/null || { echo "greptile-budget: gh CLI not found"; exit 1; }

SINCE="${1:-$(date +%Y-%m-01)}"
ORGS=(algominds-ai gainz-ai-dev)
BOT='greptile-apps%5Bbot%5D'

# Included allowance is 50 credits per ACTIVE developer, where active means anyone
# with at least one completed review charged to them in the period. Counting the
# humans who opened PRs is the closest proxy we can get without the billing API.
seats=0
for org in "${ORGS[@]}"; do
  n=$(gh api "search/issues?q=org:$org+is:pr+created:>=$SINCE&per_page=100" --paginate \
        --jq '.items[].user.login' 2>/dev/null | grep -v '\[bot\]' | sort -u | wc -l | tr -d ' ')
  seats=$((seats + n))
done

echo "Greptile spend since $SINCE"
echo

total=0
for org in "${ORGS[@]}"; do
  n=$(gh api "search/issues?q=org:$org+is:pr+commenter:$BOT+created:>=$SINCE&per_page=1" --jq .total_count 2>/dev/null)
  n=${n:-0}
  total=$((total + n))
  printf '  %-16s %4d reviewed PRs\n' "$org" "$n"
  gh api "search/issues?q=org:$org+is:pr+commenter:$BOT+created:>=$SINCE&per_page=100" --paginate \
    --jq '.items[].repository_url|split("/")|last' 2>/dev/null \
    | sort | uniq -c | sort -rn | head -8 | sed 's/^/      /'
done

allow=$((seats * 50))
echo
echo "  reviewed PRs (floor on credits) : $total"
echo "  distinct human PR authors       : $seats"
echo "  included allowance              : $allow  (${seats} x 50)"

if [ "$total" -gt "$allow" ]; then
  over=$((total - allow))
  echo
  echo "  OVER by at least $over credits. At \$1/credit that is \$${over}+ of flex, before"
  echo "  re-reviews, which this count cannot see."
  echo
  echo "  Pull the levers in greptile/COST-POLICY.md: strictness 3, greploop to 1 round,"
  echo "  and check the flex cap in app.greptile.com before the invoice does it for you."
  exit 1
fi

echo
echo "  Inside the allowance with $((allow - total)) credits of headroom."
