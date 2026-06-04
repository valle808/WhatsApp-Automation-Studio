#!/usr/bin/env python3
"""
Contact management module for WhatsApp Campaign Studio.
Handles storing, importing, exporting, and syncing contacts.
"""
import json
import os
import csv
import time
from typing import List, Optional, Tuple

CONTACTS_PATH = os.path.expanduser("~/whatsapp_campaign_contacts.json")


class Contact:
    """Represents a single contact"""
    def __init__(self, name: str, phone: str = "", tags: List[str] = None,
                 notes: str = "", synced_from_wa: bool = False):
        self.name = name
        self.phone = phone.strip()
        self.tags = tags or []
        self.notes = notes
        self.synced_from_wa = synced_from_wa

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "phone": self.phone,
            "tags": self.tags,
            "notes": self.notes,
            "synced_from_wa": self.synced_from_wa
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            synced_from_wa=data.get("synced_from_wa", False)
        )

    def display_name(self) -> str:
        if self.phone:
            return f"{self.name}  ·  {self.phone}"
        return f"{self.name}  (no phone)"

    def search_key(self) -> str:
        return f"{self.name} {self.phone} {' '.join(self.tags)}".lower()

    def __repr__(self):
        return f"Contact(name={self.name!r}, phone={self.phone!r})"


class ContactManager:
    """Manages the full lifecycle of contacts: CRUD, import/export, WA sync."""

    def __init__(self, contacts_path: str = None):
        self.contacts_path = contacts_path or CONTACTS_PATH
        self.contacts: List[Contact] = []
        self.load_contacts()

    # ─── Persistence ────────────────────────────────────────────────────────────

    def load_contacts(self) -> bool:
        """Load contacts from the JSON file."""
        try:
            if os.path.exists(self.contacts_path):
                with open(self.contacts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.contacts = [Contact.from_dict(c) for c in data]
                return True
        except Exception as e:
            print(f"[ContactManager] Error loading contacts: {e}")
        return False

    def save_contacts(self) -> bool:
        """Persist contacts to the JSON file."""
        try:
            with open(self.contacts_path, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in self.contacts], f,
                          indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ContactManager] Error saving contacts: {e}")
            return False

    # ─── CRUD ────────────────────────────────────────────────────────────────────

    def add_contact(self, name: str, phone: str = "", tags: List[str] = None,
                    notes: str = "", synced: bool = False) -> Tuple[bool, str]:
        """
        Add a new contact. Returns (success, message).
        Prevents exact duplicate phone numbers or name-only duplicates.
        """
        name = name.strip()
        phone = phone.strip()
        if not name:
            return False, "Contact name cannot be empty."
        for c in self.contacts:
            if phone and c.phone == phone:
                return False, f"A contact with phone {phone!r} already exists."
            if not phone and c.name.lower() == name.lower():
                return False, f"A contact named {name!r} already exists."

        contact = Contact(name=name, phone=phone,
                          tags=tags or [], notes=notes, synced_from_wa=synced)
        self.contacts.append(contact)
        self.save_contacts()
        return True, "Contact added."

    def update_contact(self, index: int, name: str, phone: str,
                       tags: List[str] = None, notes: str = "") -> bool:
        """Update an existing contact at the given index."""
        if 0 <= index < len(self.contacts):
            self.contacts[index].name = name.strip()
            self.contacts[index].phone = phone.strip()
            self.contacts[index].tags = tags or []
            self.contacts[index].notes = notes
            self.save_contacts()
            return True
        return False

    def remove_contact(self, index: int) -> bool:
        """Remove a single contact by index."""
        if 0 <= index < len(self.contacts):
            del self.contacts[index]
            self.save_contacts()
            return True
        return False

    def remove_contacts_by_indices(self, indices: List[int]) -> int:
        """Remove multiple contacts by index (sorted desc to avoid shifting)."""
        removed = 0
        for idx in sorted(set(indices), reverse=True):
            if 0 <= idx < len(self.contacts):
                del self.contacts[idx]
                removed += 1
        self.save_contacts()
        return removed

    def clear_all_contacts(self):
        """Delete every contact."""
        self.contacts = []
        self.save_contacts()

    def get_by_index(self, index: int) -> Optional[Contact]:
        if 0 <= index < len(self.contacts):
            return self.contacts[index]
        return None

    def get_all_contacts(self) -> List[Contact]:
        return self.contacts

    def search_contacts(self, query: str) -> List[Contact]:
        """Filter contacts by name, phone, or tags."""
        if not query:
            return self.contacts
        q = query.strip().lower()
        return [c for c in self.contacts if q in c.search_key()]

    # ─── Import / Export ─────────────────────────────────────────────────────────

    def import_from_csv(self, filepath: str) -> Tuple[int, int, List[str]]:
        """
        Import from a CSV file. Expected columns (any capitalisation):
        name, phone, tags, notes
        Returns (added_count, skipped_count, error_messages).
        """
        added, skipped, errors = 0, 0, []
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    def get(keys):
                        for k in keys:
                            v = row.get(k, "")
                            if v:
                                return v.strip()
                        return ""

                    name  = get(["name", "Name", "NAME", "contact_name", "Contact Name", "full_name"])
                    phone = get(["phone", "Phone", "PHONE", "number", "Number",
                                 "mobile", "Mobile", "whatsapp", "WhatsApp", "tel"])
                    tags_raw = get(["tags", "Tags", "TAG", "category", "Category"])
                    notes = get(["notes", "Notes", "NOTE", "comment", "Comment"])
                    tag_list = [t.strip() for t in tags_raw.split(",") if t.strip()]

                    if not name and not phone:
                        errors.append(f"Row skipped (no name or phone): {dict(row)}")
                        continue

                    success, msg = self.add_contact(name or phone, phone, tag_list, notes)
                    if success:
                        added += 1
                    else:
                        skipped += 1
                        errors.append(f"Skipped '{name}': {msg}")
        except Exception as e:
            errors.append(f"File error: {e}")
        return added, skipped, errors

    def export_to_csv(self, filepath: str) -> bool:
        """Export all contacts to a CSV file."""
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "phone", "tags", "notes"])
                for c in self.contacts:
                    writer.writerow([c.name, c.phone, ",".join(c.tags), c.notes])
            return True
        except Exception as e:
            print(f"[ContactManager] Export error: {e}")
            return False

    # ─── WhatsApp Web Sync ───────────────────────────────────────────────────────

    def sync_from_whatsapp(self, driver) -> Tuple[int, int]:
        """
        Scroll through the entire WhatsApp Web chat list and import contact
        names. Phone numbers cannot be reliably extracted here, so contacts
        are stored with name only (user can fill in phone later).

        Returns (newly_added, total_found).
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        found_names = []
        seen_in_app = {c.name for c in self.contacts}

        try:
            # Ensure we are on the main chat screen
            chat_panel = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@aria-label="Chat list"]')
                )
            )

            # Scroll to the very top first
            driver.execute_script("arguments[0].scrollTop = 0", chat_panel)
            time.sleep(0.6)

            no_change_streak = 0
            prev_scroll_top = -1

            for _ in range(80):   # max iterations to prevent infinite loop
                # Extract currently visible chat titles
                elements = driver.find_elements(
                    By.XPATH,
                    '//*[@aria-label="Chat list"]//*[@dir="auto"][@title]'
                )
                for el in elements:
                    try:
                        title = el.get_attribute("title")
                        if title and title not in seen_in_app and len(title.strip()) > 0:
                            # Filter out system items like "WhatsApp" etc.
                            if title not in ("WhatsApp", "Status", "Calls"):
                                seen_in_app.add(title)
                                found_names.append(title)
                    except Exception:
                        pass

                # Scroll down by 300 px
                driver.execute_script("arguments[0].scrollBy(0, 300)", chat_panel)
                time.sleep(0.35)

                current_top = driver.execute_script(
                    "return arguments[0].scrollTop", chat_panel
                )
                if current_top == prev_scroll_top:
                    no_change_streak += 1
                    if no_change_streak >= 4:
                        break   # reached the bottom
                else:
                    no_change_streak = 0
                prev_scroll_top = current_top

        except Exception as e:
            print(f"[ContactManager] WA sync error: {e}")

        # Persist newly found contacts
        newly_added = 0
        for name in found_names:
            success, _ = self.add_contact(name, "", [], "", synced=True)
            if success:
                newly_added += 1

        return newly_added, len(found_names)
