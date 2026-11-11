# LOOK — Generation log

Seedance 2.5 Draft (480p), 16:9, audio on, into the Higgsfield project **baba look**. A chosen draft is generated again in 1080p from its job id (`draft_job_id`).

## How the runs are submitted

The `<<<element_id>>>` placeholder is **not** resolved by Seedance 2.5; it arrives as raw text, and a run with no attached media is rejected. So each run attaches the element images directly as `image_references`, in the order of its Attach list, and every `@name` in the prompt becomes `@image1`, `@image2`… in that same order. The prompt text is otherwise unchanged. The element → media id map is in `tools/element_media.json`.

## Drafts

| Run | Draft job id | Review notes (from frames; audio not checked) | Pick for 1080p |
|---|---|---|---|
| G01 | `59d33d66-ee60-4e6a-bf9e-7b5b277b30df` | Done. Good: burner catches, blue flame, Adam from behind. Shot 2 plays wider than MS, a full kitchen seen through a door frame. | |
| G02 | `f811267b-8457-4d7a-88aa-72cf99cb66fd` | Done. Clean top shot, plate order right, yellow cup last. A knife may show at the right edge in the last frame. | |
| G03 | `6ec1e1ad-06fc-4266-8d27-1f83d192916e` | Done. Wide: the mannequins are lit and readable, not silhouettes, so the reveal comes before G04. CU of Adam is strong. | |
| G04 | `2562c11f-16c2-44cd-ac8e-5f3043f91e4a` | Done. The kiss works, but the head flips from the back of the wig to a plastic face mid-shot, as if the mannequin turned. The reveal needs a reroll. | |
| G05 | `7d8378dd-0ae5-45bf-bcc8-caca39c9396e` | Done. Strongest of the set: symmetrical, mannequins still, yellow cup and dress the only colour. | |
| G06 | `54cb9011-ef22-4f0e-8db7-3ffe56bfc00c` | Done. Works. The bread is untoasted white bread and the bin is a wooden box on legs, not a pedal bin. | |
| G07 | `756491a8-c5a8-4607-9607-7ad71bdd87ae` | Done. Usable. The bag lies on top beside the mail, not under it, and is not dusty. Push-in is very slight. | |
| G08 | `14707b46-bf7a-4b99-afce-7c05c7c9451c` | Done. Usable. Rigid foot on a metal stand, sandal buckles, freeze, hand to temple. The scar is hard to see at 480p. | |
| G09 | `f6820f1e-206d-4d62-983e-aaafc6241768` | Done. Light is right, but her mouth and chin show in shot 1, and the crayons look like capped markers. | |

Cost: 3 credits per second of draft, so 183 credits for G01–G09.
