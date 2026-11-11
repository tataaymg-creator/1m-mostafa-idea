# LOOK — Higgsfield Elements

All 33 elements live in the Higgsfield project **baba look**. Every image is 16:9. In a prompt, call an element by its name with `@`, for example `@adam` or `@L02_dining`. Which elements each generation needs is listed in [`prompts.md`](prompts.md).

## How consistency was built

- One living-room image is the master. The dining room, sewing corner, hallway and landing were generated from it, and the kitchen from the dining-room image, so the kitchen matches what is seen through the doorway.
- Fixed props are baked into the location images: the radio in the kitchen, the rabbit, night-light and crayons in Nour's room, the bag on the hallway console, the crayons in the car.
- Moving props stay separate elements: cup, plates, sandal, brush, dish, watch, bag contents, drawing, car exterior.
- The watch comes from Layla's sheet; the bag contents from the watch, crayons and drawing; the sealed bag from the contents.
- Two hallways: `L05b_hallway-bag` until the bag is opened (shot 72), `L05_hallway` after.

## Characters

| Element | What | Element id |
|---|---|---|
| `adam` | Adam, present day: scar, stubble, grey-blue shirt, bare feet | `9c70b944-13a8-4231-93db-404db1428192` |
| `adam-before` | Adam in the memory: no scar, shaved, linen shirt, no sunglasses | `bfb6bcd3-e1df-4cdb-9d4d-fb1e5aadaad1` |
| `layla` | Layla, the wife (memory only) | `e712cf1e-37e2-40f8-b6a7-199f095de10b` |
| `nour` | Nour, the daughter, 6 (memory only) | `c28a7770-b7af-4503-a6a5-ee7e13731382` |
| `mona` | Mona, Layla's older sister | `fc203cad-8f11-4cb7-af5d-9f7e3aaeee2f` |
| `doll-wife` | Adult mannequin in Layla's burgundy cardigan | `31a8cb88-f0e0-40b5-ac7c-f17e5e7caa36` |
| `doll-daughter` | Child mannequin in the unfinished yellow dress | `28cdcfad-7312-4812-ac4e-a0215f63b939` |

## Locations

| Element | What | Element id |
|---|---|---|
| `L01_kitchen` | Kitchen, radio on the shelf; matches the view through the dining-room doorway | `dae8d77b-2383-48d9-9884-26fa1c3c45d2` |
| `L02_dining` | Dining table in front of the closed curtains | `c367b428-e15b-40a4-a5f6-f6a7034bd470` |
| `L03_living-room` | Living room master, curtains closed | `56e98e89-8ed1-4031-9af0-6bf3763ebdb7` |
| `L03b_living-day` | Living room, curtains open, morning sun | `da4c8ed4-3e9c-45af-b85a-16a58a215205` |
| `L04_sewing-corner` | Sewing corner of the living room, framed mirror, two empty stands | `a1c9ec16-9d46-4a1d-925a-c97432ca6b8a` |
| `L05_hallway` | Hallway and front door, no bag on the console | `a4efce0c-da8f-44b2-9d7b-c8d35de1e3bb` |
| `L05b_hallway-bag` | Hallway with the sealed bag on the console (use until the bag is opened) | `3aac8199-6966-4d91-a3df-f0e9630570d1` |
| `L06_nour-room` | Nour's bedroom at night: rabbit, star light, crayons at true size | `d7ca253d-c850-41c7-b93a-b9cfc1c39f56` |
| `L07_car-front` | Car interior from the back seat, looking forward at the road | `849653b9-b12e-4156-a6fb-83fe988cff6b` |
| `L07b_car-backseat` | Car back seat: book, paper, small crayons, swim ring | `c05fb424-4cb2-405d-b4ba-94c16bec6648` |
| `L08_desert-road` | Desert highway toward the sea, golden hour | `fed473d5-0634-40e9-8c22-80aa4f4271a2` |
| `L09_landing` | Stairwell landing outside the door | `50656263-4442-47a6-aa31-966ea97d1f1c` |

## Props

| Element | What | Element id |
|---|---|---|
| `P01_yellow-cup` | Nour's yellow plastic cup | `dde5ccb9-b901-458e-8c3f-1ea163e10762` |
| `P02_table-setting` | Three plates and three forks | `bc49dca7-2b90-4758-b200-10564e600be6` |
| `P03_yellow-sandal` | Yellow child's sandal with a buckle | `9e5f729c-240b-410b-9964-c5629f0a2a92` |
| `P04_hairbrush` | Worn wooden hairbrush | `72ee01a4-8fef-4a66-b07f-4e10698b33b6` |
| `P05_radio` | Old portable radio | `3f1a4502-93ab-4d5a-bea3-e0216e994637` |
| `P06_hospital-bag` | Sealed hospital bag, made from the contents image | `75c935d8-b381-4807-9491-59b501c25bc7` |
| `P07_bag-contents` | Bag contents, made from the watch, crayons and drawing | `824a3b56-a588-4db2-a93e-b65af81301d5` |
| `P08_layla-watch` | Layla's gold watch, cracked, taken from her character sheet | `5859adcb-6cb1-4ab3-bf5b-58d85d030a6e` |
| `P09_drawing` | Nour's crayon drawing | `b079b600-d8a5-42f6-8165-a7b82587d41b` |
| `P10_rabbit` | Worn grey stuffed rabbit | `e128d8c3-b571-4a6c-8bd7-fc4b2756a3d7` |
| `P11_night-light` | Star-projector night-light | `52aa9996-7eda-4d94-a233-e0a85b40f505` |
| `P12_crayons` | Worn wax crayons, yellow shortest | `85400f0e-6618-4491-9ee9-4c9c71627b4d` |
| `P13_family-car` | Off-white family sedan, exterior | `b9330f8f-d81c-4b45-9390-079c60787c45` |
| `P14_foil-dish` | Mona's foil-covered dish | `10082eb8-4c5e-4253-a10a-c9d9eb6adc38` |

Images are saved in [`characters/`](characters/), [`locations/`](locations/) and [`props/`](props/).
