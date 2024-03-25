#!/usr/bin/env python3

import argparse
import json
from colorama import init, Fore, Style
import glob
import os
import subprocess
parser = argparse.ArgumentParser(description="Code Review Command Line Tool")

subparsers = parser.add_subparsers(dest="command", help="Available commands")

start_parser = subparsers.add_parser("start", help="Start a code review session")
start_parser.add_argument("issue_id", type=str, help="Issue ID for the code review session")


list_parser = subparsers.add_parser("list", help="List all code reviews")

complete_parser = subparsers.add_parser("complete", help="Mark a checklist item as completed")
complete_parser.add_argument("issue_id", type=str, help="Issue ID for the code review session")
complete_parser.add_argument("index", type=int, help="Index of the checklist item to mark as completed")

customize_parser = subparsers.add_parser("customize", help="Customize the default checklist")

remove_parser = subparsers.add_parser("status", help="Show a code review status based on Issue ID")
remove_parser.add_argument("issue_id", type=str, help="Issue ID of the code review")

remove_parser = subparsers.add_parser("remove", help="Remove a code review based on Issue ID")
remove_parser.add_argument("issue_id", type=str, help="Issue ID of the code review to remove")

args = parser.parse_args()

DEFAULT_CHECKLIST = [
    {"description": "Code follows coding standards and style guidelines", "completed": False},
    {"description": "Code is well-commented and easy to understand", "completed": False},
    {"description": "Code is modular, reusable, and maintainable", "completed": False},
    {"description": "Code is properly tested, including unit tests and integration tests", "completed": False},
    {"description": "Code handles edge cases and error conditions gracefully", "completed": False},
    {"description": "Code adheres to security best practices and is free from vulnerabilities", "completed": False},
    {"description": "Code has been reviewed for performance optimizations", "completed": False},
    {"description": "Code documentation is up-to-date and comprehensive", "completed": False},
    {"description": "Code changes have been reviewed for impact on existing functionality", "completed": False},
    {"description": "Code changes have been reviewed for backward compatibility", "completed": False}
]

def load_checklist_config():
    config_file = "checklist_config.json"
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return DEFAULT_CHECKLIST

def load_checklist(issue_id):
    try:
        with open(f"data/{issue_id}_checklist.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_checklist(issue_id, checklist):
    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    with open(f"data/{issue_id}_checklist.json", "w") as file:
        json.dump(checklist, file, indent=4)

def start_review(issue_id):
    print(f"Starting code review session for Issue ID: {issue_id}")
    checklist = load_checklist(issue_id)
    if not checklist:
        print("No checklist found. Using default checklist.")
        checklist = load_checklist_config()
        save_checklist(issue_id, checklist)
    display_checklist(checklist)
    return checklist

def complete_item(issue_id, index):
    checklist = load_checklist(issue_id)
    if 0 <= index < len(checklist) + 1:
        checklist[index-1]["completed"] = True
        save_checklist(issue_id, checklist)
        print(f"Item {index} marked as completed.")
        display_checklist(checklist)
        if all(item["completed"] for item in checklist):
            print(Fore.GREEN + Style.BRIGHT + f"\n CODE REVIEW COMPLETED FOR JIRA ID: {issue_id}\n")
    else:
        print("Invalid item index.")

def review_status(issue_id):
    checklist = load_checklist(issue_id)
    if not checklist: 
        print(f"Issue ID: {issue_id} | State: Not found")
        return
    state = get_review_state(checklist)
    print(f"Issue ID: {issue_id} | State: {state}")
    display_checklist(checklist)

def save_checklist_config(checklist):
    config_file = "checklist_config.json"
    with open(config_file, "w") as file:
        json.dump(checklist, file, indent=4)


def customize_checklist():
    checklist = load_checklist_config()
    print("Opening checklist editor...")
    editor = os.environ.get('EDITOR', 'vim')  # Use vim editor by default if EDITOR environment variable is not set
    subprocess.run([editor, "checklist_config.json"])
    updated_checklist = load_checklist_config()
    if checklist != updated_checklist:
        save_checklist_config(updated_checklist)
        print("Checklist updated successfully.")
    else:
        print("No changes made to the checklist.")


def display_checklist(checklist):
    print("Code Review Checklist:")
    print("----------------------")
    for i, item in enumerate(checklist, start=1):
        print(f"{i}. {'[X]' if item['completed'] else '[ ]'} {item['description']}")

def get_review_state(checklist):
    if all(item["completed"] for item in checklist):
        return "Completed"
    else:
        return "Ongoing"

def list_reviews():
    print("Listing all code reviews:")
    print("------------------------")
    for filename in glob.glob("data/*_checklist.json"):
        issue_id = filename.split("_")[0][5:]
        checklist = load_checklist(issue_id)
        state = get_review_state(checklist)
        print(f"Issue ID: {issue_id} | State: {state}")

def remove_review(issue_id):
    checklist_file = f"data/{issue_id}_checklist.json"
    if os.path.exists(checklist_file):
        os.remove(checklist_file)
        print(f"Code review with Issue ID '{issue_id}' removed successfully.")
    else:
        print(f"No code review found with Issue ID '{issue_id}'.")

if args.command == "start":
    start_review(args.issue_id)
elif args.command == "list":
    list_reviews()
elif args.command == "status":
    review_status(args.issue_id)
elif args.command == "complete":
    complete_item(args.issue_id, args.index)
elif args.command == "customize":
    customize_checklist()
elif args.command == "remove":
    remove_review(args.issue_id)
else:
    print("Invalid command. Please try again.")

