import pywikibot
import os
import re
import sys
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fuzzywuzzy import fuzz

# fork of original itn.py, for saving all the archive/entries to local files by month name.

site = pywikibot.Site("en", "wikipedia")
#source_page = pywikibot.Page(site, "User:KiranBOT/sandbox")
source_page = pywikibot.Page(site, "Template:In the news")
archive_index_page_title = "Wikipedia:In the news/Posted/Archives"

log_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "itn_out.txt")
#open(log_file, "w", encoding='utf-8').close()

def format_timestamp(timestamp):
    formatted_timestamp = timestamp.strftime("%H:%M, %d %B %Y")
    return formatted_timestamp

current_date = datetime.now()
current_month_name = current_date.strftime("%B")
current_year = current_date.strftime("%Y")
archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{current_month_name} {current_year}.txt")

prev_date = current_date - relativedelta(months=2)
prev_month_name = prev_date.strftime("%B")
prev_year = prev_date.strftime("%Y")
prev_archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{prev_month_name} {prev_year}.txt")

revisions = list(source_page.revisions(content=True))[::-1] # for the total past archive/one time run
#revisions = list(source_page.revisions(total=50, content=True))[::-1] # for daily cron
#revisions = list(source_page.revisions(total=500, content=True))[::-1]

#archive_page = pywikibot.Page(site, archive_page_title)

edit_counter = 0

for revision in revisions:
    old_revision_id = revision.parentid
    new_revision_id = revision.revid
    new_revision_id_str = str(new_revision_id)
    timestamp = revision.timestamp
    editor_name = revision.user

    prev_month = timestamp - relativedelta(months=2)
    prev_month_name = prev_month.strftime("%B")
    prev_year = prev_month.strftime("%Y")
    prev_archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{prev_month_name} {prev_year}.txt")

    current_month_changes = []
    prev_month_changes = []
    prev_archive_lines = []

    try:
        diff = site.compare(old_revision_id, new_revision_id)
        soup = BeautifulSoup(diff, "html.parser")
        added_elements = soup.find_all("td", class_="diff-addedline diff-side-added")

        # Process additions
        for added_element in added_elements:
            div_elements = added_element.find_all("div")
            for div_element in div_elements:
                text_content = div_element.get_text()

                #if not text_content.startswith("| ") and not text_content.startswith("[[Image:"):
                if not (text_content.startswith("| ") or text_content.startswith(" |") or text_content.startswith("[[Image:")):
                        editor_name = revision.user
                        formatted_timestamp = format_timestamp(timestamp)
                        text_content = text_content.replace("*[[", "*'''RD''' [[").replace("* [[", "*'''RD''' [[")
                        text_content = re.sub(r'\*{{nowrap\|\[\[(.*?)\]\]}}', r"*'''RD''' [[\1]]", text_content)
                        text_content = re.sub(r'\*{{\*mp\|(.*?)}}', r'*<!--\1-->', text_content)
                        formatted_timestamp = format_timestamp(timestamp)

                        date_parts = formatted_timestamp.split(", ")
                        if len(date_parts) >= 2:
                            timestamp_time = date_parts[0]
                            day_month_year = date_parts[1].split(" ")  
                            day = int(day_month_year[0])
                            month_name = day_month_year[1]
                            year = day_month_year[2]
                            day_month_header = f"{month_name} {day}"
                            #archive_page_title = f"Wikipedia:In the news/Posted/{month_name} {year}"
                            #archive_page_title = f"User:KiranBOT/sandbox/Posted/{month_name} {year}"
                            archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{month_name} {year}.txt")

                            if not os.path.exists(archive_file):
                                open(archive_file, "w", encoding='utf-8').close()
                                with open(archive_file, "a", encoding='utf-8') as f:
                                    #f.write(f"{{Wikipedia:In the news/Posted/Archives/header}}\n")
                                    f.write("{{{{Wikipedia:In the news/Posted/Archives/header}}}}\n")
                                edit_counter += 1
                                #time.sleep(3)

                                # get archive page title
                                #archive_page_title = f"Wikipedia:In the news/Posted/{month_name} {year}"
                                archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{month_name} {year}.txt")

                                # get archive index page content
                                #archive_index_page = pywikibot.Page(site, archive_index_page_title)
                                #archive_index_text = archive_index_page.text

                                # Find the line that contains <!-- End archive links -->
                                #lines = archive_index_text.splitlines()
                                #end_archive_line = None
                                #for i, line in enumerate(lines):
                                    #if "<!-- End archive links -->" in line:
                                        #end_archive_line = i
                                        #break

                                # add the new archive link to the same line as the existing archive links
                                #if end_archive_line is not None:
                                    #new_archive_link = f"[[Wikipedia:In the news/Posted/{month_name} {year}|{month_name} {year}]]"
                                    #lines[end_archive_line - 1] += f" &bull; {new_archive_link}"

                                # join the lines back together
                                #archive_index_text = '\n'.join(lines)

                                # regex pattern to find the January link and replace it with a newline
                                #january_link_pattern = r']] &bull; \[\[Wikipedia:In the news/Posted/January(.*?)]]'
                                # replace with newline
                                #archive_index_text = re.sub(january_link_pattern, r']]\n* [[Wikipedia:In the news/Posted/January\1]]', archive_index_text)

                                # save the updated archive index page
                                #archive_index_page.text = archive_index_text
                                #archive_index_page.save(f"updated archive page", minor=True, botflag=True)
                                #edit_counter += 1
                                #time.sleep(3)
                                ####
                                ####

                            header = f"== {day_month_header} =="
                            with open(archive_file, "r+", encoding="utf-8") as file:
                                content = file.read()

                                if header not in content:
                                    content += "\n" + header
                                    file.seek(0)
                                    file.write(content)
                                    file.truncate()

                            entry_found_current = False
                            entry_found_previous = False

                            archive_lines = open(archive_file).read().split("\n")
                            regex_pattern = re.compile(re.escape(text_content[:30]), re.IGNORECASE) # regardless the similarity ratio, token based/fuzzy match is not effective here
                            last_matching_index = -1

                            for i, line in enumerate(archive_lines):
                                if regex_pattern.search(line):
                                    last_matching_index = i
                                    entry_found_current = True

                            if entry_found_current:
                                if new_revision_id_str in open(archive_file).read():
                                    continue  # Skip this revision and move to the next one
                                update_message = f" <small>[[special:diff/{new_revision_id}|updated]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                                current_month_changes.insert(last_matching_index + 1, text_content + update_message)
                            else:
                                # check previous month's page
                                prev_month = timestamp - relativedelta(months=1)
                                prev_month_name = prev_month.strftime("%B")
                                prev_year = prev_month.strftime("%Y")
                                prev_archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{prev_month_name} {prev_year}.txt")

                                if os.path.isfile(prev_archive_file):
                                    last_matching_index_prev = -1
                                    prev_archive_lines = open(prev_archive_file).read().split("\n")

                                for i, line in enumerate(prev_archive_lines):
                                    if regex_pattern.search(line):
                                        last_matching_index_prev = i
                                        entry_found_previous = True

                                if entry_found_previous:
                                    if new_revision_id_str in open(prev_archive_file).read():
                                        continue  # Skip this revision and move to the next one
                                    update_message = f" <small>[[special:diff/{new_revision_id}|updated]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                                    prev_archive_lines.insert(last_matching_index_prev + 1, f"{text_content} {update_message}")
                                    prev_month_changes.insert(last_matching_index + 1, text_content + update_message)
                                elif not entry_found_current and not entry_found_previous:
                                    if new_revision_id_str in open(archive_file).read():
                                        continue
                                    update_message = f" <small>[[special:diff/{new_revision_id}|added]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                                    current_month_changes.append(text_content + update_message)
        
        #for change in current_month_changes:
            #with open(archive_file, "a", encoding="utf-8") as file:
                #file.write("\n" + change)

        ####
        #### Process removals
        ####
        
        # define similarity percentage fuzz.token_sort_ratio
        def token_match_percentage(str1, str2):
            return fuzz.token_sort_ratio(str1, str2)

        SIMILARITY_THRESHOLD = 70  # Adjust as per requirements

        removed_elements = soup.find_all("td", class_="diff-deletedline diff-side-deleted")
        for removed_element in removed_elements:
            div_elements = removed_element.find_all("div")
            for div_element in div_elements:
                text_content = div_element.get_text()

                #if not text_content.startswith("| "):
                if not (text_content.startswith("| ") or text_content.startswith(" |") or text_content.startswith("[[Image:")):
                    editor_name = revision.user
                    formatted_timestamp = format_timestamp(timestamp)

                    date_parts = formatted_timestamp.split(", ")
                    if len(date_parts) >= 2:
                        timestamp_time = date_parts[0]
                        day_month_year = date_parts[1].split(" ")  
                        day = int(day_month_year[0])
                        month_name = day_month_year[1]
                        year = day_month_year[2]
                        day_month_header = f"{month_name} {day}"

                    text_content = text_content.replace("*[[", "*'''RD''' [[").replace("* [[", "*'''RD''' [[")
                    text_content = re.sub(r'\*{{nowrap\|\[\[(.*?)\]\]}}', r"*'''RD''' [[\1]]", text_content)
                    text_content = re.sub(r'\*{{\*mp\|(.*?)}}', r'*<!--\1-->', text_content)

                    # get new revision content
                    new_revision_id_str = str(new_revision_id)
                    revision_content = source_page.getOldVersion(oldid=new_revision_id)
                    new_revision_content = revision_content.split("\n")
                    
                    # check if the removed content is actual removal, or an update
                    is_update = any(token_match_percentage(text_content, new_line) >= SIMILARITY_THRESHOLD for new_line in new_revision_content)
                    
                    # if its an update, skip the removal process
                    if is_update:
                        continue

                    # process the removal, as it is not an update
                    match_length = 15 if text_content.startswith("*'''RD''' [[") else 30
                    archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{month_name} {year}.txt")
                    regex_pattern = re.compile(re.escape(text_content[:match_length]), re.IGNORECASE)
                    last_matching_index = -1

                    with open(archive_file, "r", encoding="utf-8") as file:
                        archive_lines = file.read().split("\n")

                    for i, line in enumerate(archive_lines):
                        if regex_pattern.search(line):
                            last_matching_index = i

                    if last_matching_index != -1:
                        update_message = f"<small>[[special:diff/{new_revision_id}|removed]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                        if text_content.startswith("*'''RD''' [["):
                            if last_matching_index < len(archive_lines):
                                archive_lines[last_matching_index] += update_message
                        else:
                            archive_lines.insert(last_matching_index + 1, f"{text_content} {update_message}")
                        with open(archive_file, "w", encoding="utf-8") as file:
                            file.write("\n".join(archive_lines))
                        current_month_changes.append(text_content)
                    else:
                        prev_month = timestamp - relativedelta(months=1)
                        prev_month_name = prev_month.strftime("%B")
                        prev_year = prev_month.strftime("%Y")
                        prev_archive_file = os.path.join(os.path.expanduser("~"), "enwiki", "itn", "local", "archives", f"{prev_month_name} {prev_year}.txt")

                        if os.path.isfile(prev_archive_file):
                            with open(prev_archive_file, "r", encoding="utf-8") as file:
                                prev_archive_lines = file.read().split("\n")

                            last_matching_index_prev = -1
                            for i, line in enumerate(prev_archive_lines):
                                if regex_pattern.search(line):
                                    last_matching_index_prev = i

                            if last_matching_index_prev != -1:
                                update_message = f"<small>[[special:diff/{new_revision_id}|removed]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                                if text_content.startswith("*'''RD''' [["):
                                    if last_matching_index_prev < len(prev_archive_lines):
                                        prev_archive_lines[last_matching_index_prev] += update_message
                                else:
                                    prev_archive_lines.insert(last_matching_index_prev + 1, f"{text_content} {update_message}")
                            else:
                                # If the removed entry is not found in both the current and the previous archive pages
                                update_message = f"<small>[[special:diff/{new_revision_id}|removed]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                                current_month_changes.append(f"{text_content} {update_message}")

                            with open(prev_archive_file, "w", encoding="utf-8") as file:
                                file.write("\n".join(prev_archive_lines))
                        else:
                            # If the removed entry is not found in both the current and the previous archive pages
                            update_message = f"<small>[[special:diff/{new_revision_id}|removed]] by [[User:{editor_name}|{editor_name}]], {formatted_timestamp}</small>"
                            current_month_changes.append(f"{text_content} {update_message}")

        # Save the changes to local files
        if current_month_changes:
            with open(archive_file, "a", encoding="utf-8") as file:
                for change in current_month_changes:
                    file.write("\n" + change)
            edit_counter += 1
            # time.sleep(3)

        if prev_month_changes:
            with open(prev_archive_file, "a", encoding="utf-8") as file:
                for change in prev_month_changes:
                    file.write("\n" + change)
            edit_counter += 1
            # time.sleep(3)

        if edit_counter >= 50:
            sys.exit()  # Exit the script

    except Exception as e:
        #print(f"Error: {e}")
        with open(log_file, "a") as f:
            f.write(f"* {e}\n")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(log_file, "a") as f:
    f.write(f"* exiting, {edit_counter} total edits at {current_time}.")
