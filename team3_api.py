#!/usr/bin/env python3
"""
Team 3 (Crawler Gamma) - Server-side API Deploy Script
Adds bulkImport endpoint to BusinessController.php on the SomeKorean server.

Usage:
    python team3_api.py
    python team3_api.py --dry-run         # Preview changes without writing
    python team3_api.py --routes-only     # Only append route note
"""

import os
import sys
import argparse
from pathlib import Path

# ─── Paths (adjust if server layout differs) ─────────────────────────────────
BUSINESS_CONTROLLER_PATH = "/var/www/somekorean/app/Http/Controllers/BusinessController.php"
ROUTES_NOTES_PATH        = "/var/www/somekorean/ROUTES_TO_ADD.md"
LOCAL_CONTROLLER_PATH    = "BusinessController.php"   # fallback for local test

# ─── PHP method to inject ─────────────────────────────────────────────────────
BULK_IMPORT_METHOD = r'''
    /**
     * Bulk import businesses from crawler.
     * POST /api/admin/businesses/import
     * Requires: admin middleware + Bearer token
     */
    public function bulkImport(Request $request)
    {
        $businesses = $request->input('businesses', []);
        if (empty($businesses)) {
            return response()->json(['error' => 'No businesses provided'], 422);
        }

        $inserted = 0; $skipped = 0; $updated = 0;
        foreach ($businesses as $biz) {
            if (empty($biz['name_en']) && empty($biz['name_ko'])) { $skipped++; continue; }

            $name    = $biz['name_en'] ?? $biz['name_ko'] ?? '';
            $address = $biz['address'] ?? '';

            // Check for duplicates by name + address
            $existing = \DB::table('businesses')
                ->where('name', $name)
                ->where('address', $address)
                ->first();

            if ($existing) { $skipped++; continue; }

            \DB::table('businesses')->insert([
                'name'        => $name,
                'name_ko'     => $biz['name_ko']     ?? null,
                'name_en'     => $biz['name_en']     ?? null,
                'category'    => $biz['category']    ?? '기타',
                'address'     => $address,
                'phone'       => $biz['phone']       ?? null,
                'website'     => $biz['website']     ?? null,
                'lat'         => $biz['lat']         ?? null,
                'lng'         => $biz['lng']         ?? null,
                'region'      => $biz['region']      ?? null,
                'data_source' => 'crawler',
                'source_url'  => $biz['source_url']  ?? null,
                'status'      => 'active',
                'created_at'  => now(),
                'updated_at'  => now(),
            ]);
            $inserted++;
        }

        return response()->json([
            'inserted' => $inserted,
            'updated'  => $updated,
            'skipped'  => $skipped,
            'total'    => count($businesses),
        ]);
    }
'''

# ─── Route note to append ─────────────────────────────────────────────────────
ROUTE_NOTE = (
    "\n## Team 3 Crawler Import Route\n"
    "Add the following line to `routes/api.php` inside the `admin` middleware group:\n\n"
    "```php\n"
    "Route::post('admin/businesses/import', [BusinessController::class, 'bulkImport']);  // admin middleware\n"
    "```\n"
    "\nExample middleware group:\n"
    "```php\n"
    "Route::middleware(['auth:sanctum', 'admin'])->group(function () {\n"
    "    // ... existing admin routes ...\n"
    "    Route::post('admin/businesses/import', [BusinessController::class, 'bulkImport']);\n"
    "});\n"
    "```\n"
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def inject_method_into_controller(filepath: str, dry_run: bool = False) -> bool:
    """
    Injects bulkImport() before the final closing brace of the PHP class.
    Safe: only injects if the method does not already exist.
    """
    if not os.path.exists(filepath):
        print(f"[WARN] Controller not found: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()

    if 'bulkImport' in content:
        print(f"[SKIP] bulkImport already exists in {filepath}")
        return True

    # Find last closing brace of the class
    last_brace = content.rfind('}')
    if last_brace == -1:
        print(f"[ERROR] Could not find closing brace in {filepath}")
        return False

    new_content = content[:last_brace] + BULK_IMPORT_METHOD + '\n}\n'

    if dry_run:
        print(f"[DRY-RUN] Would inject bulkImport into {filepath}")
        print("─" * 60)
        print(BULK_IMPORT_METHOD)
        print("─" * 60)
        return True

    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write(new_content)

    print(f"[OK] Injected bulkImport into {filepath}")
    return True


def append_route_note(filepath: str, dry_run: bool = False) -> bool:
    """Appends the route instruction to the notes file (creates if missing)."""
    if dry_run:
        print(f"[DRY-RUN] Would append route note to {filepath}")
        print(ROUTE_NOTE)
        return True

    try:
        Path(os.path.dirname(filepath)).mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a', encoding='utf-8') as fh:
            fh.write(ROUTE_NOTE)
        print(f"[OK] Route note appended to {filepath}")
        return True
    except PermissionError:
        print(f"[WARN] No write permission for {filepath} — printing note instead:")
        print(ROUTE_NOTE)
        return False
    except Exception as e:
        print(f"[ERROR] Could not write to {filepath}: {e}")
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Team 3: Deploy bulkImport API endpoint to BusinessController.php'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without writing to disk')
    parser.add_argument('--routes-only', action='store_true',
                        help='Only append the route note, skip controller patch')
    parser.add_argument('--controller', default=None,
                        help=f'Path to BusinessController.php (default: {BUSINESS_CONTROLLER_PATH})')
    parser.add_argument('--routes-file', default=None,
                        help=f'Path to routes notes file (default: {ROUTES_NOTES_PATH})')
    args = parser.parse_args()

    controller_path = args.controller or BUSINESS_CONTROLLER_PATH
    routes_path     = args.routes_file or ROUTES_NOTES_PATH

    # Fallback to local copy for development
    if not os.path.exists(controller_path) and os.path.exists(LOCAL_CONTROLLER_PATH):
        print(f"[INFO] Server path not found, using local: {LOCAL_CONTROLLER_PATH}")
        controller_path = LOCAL_CONTROLLER_PATH

    print("=" * 60)
    print("Team 3 (Crawler Gamma) — API Deploy Script")
    print("=" * 60)

    if not args.routes_only:
        ok = inject_method_into_controller(controller_path, dry_run=args.dry_run)
        if not ok:
            print("[ERROR] Controller injection failed.")
            if not args.dry_run:
                print("        Falling back to printing the method:")
                print(BULK_IMPORT_METHOD)

    append_route_note(routes_path, dry_run=args.dry_run)

    print("\n[DONE] Team 3 deploy script complete.")
    print("\nNext steps:")
    print("  1. Add the route to routes/api.php (see ROUTES_TO_ADD.md)")
    print("  2. Run: php artisan route:cache")
    print("  3. Set SK_API_TOKEN in crawler/.env")
    print("  4. Run: python crawler/main.py --all --import")


if __name__ == '__main__':
    main()
