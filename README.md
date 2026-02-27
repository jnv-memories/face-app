# Acknowledgement
Aur bkl vaibhav dhanyavad ye kaam karne ke liye. ye setup guide nahi hai setup guide ke liye mujhse hi contact karna parega. 
Niche ka content AI generated hai aur mera man nahi kar rha pura parne ka to koi garbar lage to mujhe contact kare. 
Thanking you
Your father
Aayush

# Face Naming Guide

This document explains how naming works in the project. It is meant for
users who are running the system for the first time and need to
understand how to correctly label faces and avoid duplicates.

## 1) How the system identifies a person

Every person in the system is stored using three things:

-   A canonical name (main name)
-   A list of aliases (alternative names)
-   Face embeddings (mathematical representation of that face)

Example structure:

    "jatin singh": {
      "aliases": ["jatin singh", "jatin"],
      "embeddings": [...]
    }

The canonical name is the main identity. Aliases are just alternative
names that refer to the same person.

## 2) When the system automatically matches a face

If the system recognizes a face with high similarity, it will print:

    [MATCHED] → jatin singh

In this case, no action is required. The face has already been
identified correctly.

## 3) When the system says "\[NEW FACE\]"

If the system cannot confidently match a face, it will ask:

    Enter canonical full name (comma aliases allowed):

At this point, you must decide whether:

-   This is an existing person
-   This is a completely new person

## 4) If the face belongs to an existing person

If the person already exists in the system, simply type their name.

You may type:

-   Full name (recommended)
-   First name only (if it is unique)
-   Any alias that already exists

If the stored person is:

    "jatin singh"

You can type:

    jatin singh

or

    jatin

The system will attach the new face embedding to the existing person.

This is normal and helps improve recognition accuracy for different
angles and lighting conditions.

## 5) If the system asks for a name that you already entered earlier

This can happen if:

-   The face angle is very different
-   Lighting conditions changed
-   The similarity score was slightly below threshold

If it is the same person, just enter the same canonical name again.

The system will add another embedding to that person, which improves
future recognition.

This is expected behavior.

## 6) If this is a completely new person

Type the full name.

It is strongly recommended to include both:

-   Full name
-   Short name or nickname

Example:

    jatin singh, jatin

This creates a canonical entry of "jatin singh" and stores "jatin" as an
alias.

This makes future matching easier and safer.

## 7) How aliases work

Aliases allow the same person to be referenced using different names.

Example:

    Enter canonical full name (comma aliases allowed):
    jatin singh, jatin, jat

Now all of these names refer to the same person:

-   jatin singh
-   jatin
-   jat

If later you type any of those, the system will attach to the same
canonical identity.

Aliases do not affect automatic face recognition. They only affect
manual name attachment.

## 8) If two people share the same first name

Example:

-   rahul verma
-   rahul sharma

If you type only:

    rahul

The system may attach to the first matching canonical it finds.

To avoid mistakes, always type the full name when multiple people share
the same first name.

Example:

    rahul verma

This ensures correct attachment.

## 9) If you type a slightly different spelling

Example:

Stored:

    jatin singh

You type:

    jatin sing

If the first name matches and embeddings are similar, it will attach
correctly.

If embeddings are extremely similar but the name is slightly different,
the system may auto-merge the entries.

This prevents duplicate identities for the same person.

## 10) If you type a completely different full name

Example:

Stored:

    jatin singh

You type:

    jatin kumar

Since the full name is different, the system will create a new canonical
identity.

This is correct behavior.

## 11) Metadata writing behavior

After all faces in an image are processed:

If the image has three or fewer people: - The system stores full
canonical names and aliases in Drive metadata.

If the image has more than three people: - The system stores only the
first name of each canonical to avoid Drive metadata limits.

This does not affect recognition accuracy. It only affects how names are
stored in Drive.

## 12) Resume safety

If the program is stopped midway:

-   Already processed images are stored in processed_drive_files.json
-   Restarting the program will skip those images
-   Naming database remains intact

You will not lose previously saved identities.

## 13) Best practice for naming

Always follow this rule when creating a new person:

Type:

    Full Name, short name

Example:

    gaurav arya, gaurav

This prevents duplicate entries and ensures smooth future recognition.
