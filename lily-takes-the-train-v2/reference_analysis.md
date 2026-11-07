# Lily v2: reference analysis and look-development acceptance

## Basis and scope

This analysis uses `reference_close.jpg`, the sampled reference contact sheet,
and the previous finished film's contact sheet and focused frames. Proportions
below are practical visual targets estimated from those images, not exact
measurements of an unavailable reference mesh. The aim is a convincing adult
woman in the same general presentation. An identical identity or rig cannot
be promised without the original character asset.

The reference succeeds because an appealing adult performance sits inside a
soft, believable photographic scene. The face, body, hair, camera, surface
response, lighting, and restrained acting must work together. A recolored
child-proportioned asset will still read as a child.

## Character proportions and face

| Feature | Target for the new model | Visible failure in the previous Ellie version |
| --- | --- | --- |
| Age impression | Clearly a young adult, approximately late twenties to thirties; relaxed and capable | Very youthful face, small torso, oversized eyes/head, shorts and large boots combine into a child/adolescent impression |
| Full-body proportion | Start around 6.5–7 head lengths from skull crown to sole; use 1.65–1.72 m as a consistent working height | Approximately 4–5 head-length impression, made shorter by the large hair silhouette and boots |
| Shoulder width | Approximately 1.7–2 skull widths, with an adult shoulder/chest silhouette and natural collarbones | Narrow shoulders under a large round head; toy-like silhouette |
| Skull and face | Oval head, modestly longer than it is wide; cheeks soften into a tapered jaw and a definite chin | Nearly round face, extremely small lower-face features, long thin neck |
| Eyes | Almond-shaped lids; approximate opening width 0.17–0.20 of face width per eye, height about 0.5–0.65 of opening width; adjust in the final camera | Large circular white openings dominate the face; wide-eyed surprise persists even during neutral speech |
| Iris and pupil | Brown iris, upper portion naturally covered by upper lid; minimal white visible below the iris at rest; coherent shared gaze | Exposed round whites and rapidly shifting pupils can look startled or unfocused |
| Eyebrows | Medium-thick dark brows with a soft natural arch; neutral inner brow, small motion during emphasis | High/angled brows and open eyes make ordinary lines look worried |
| Nose | Visible bridge, side planes, nostrils and a softly rounded tip; approximately 0.20–0.24 of face height as an initial proportion target | Tiny flat button nose contributes strongly to the child read |
| Mouth and lips | Defined philtrum, subtle cupid's bow, visible lip volume; mouth width about 0.33–0.40 of face width; gentle resting smile | Small slit or large dark gape, with less readable adult lip shape |
| Smile and speech | Warm cheek lift, restrained corner lift, occasional upper-teeth glimpse; lip shapes change without losing the overall friendly expression | Mouth opening alone did most of the acting; neutral frames often looked sad or alarmed |
| Neck and shoulders | Natural adult neck width and length, shoulders relaxed and slightly asymmetric | Long thin cylindrical neck exaggerates the doll-like impression |

Treat these numbers as starting points. Acceptance comes from the neutral,
smile, and three-quarter comparison images, rather than forcing every number
onto a model. The eyes should remain stylized and expressive; they should not
become small realistic eyes in an otherwise cartoon face.

## Hair

- Dark brown, loose, shoulder-length hair with a slightly off-center part.
- Hair ends sit around the neck/shoulder line. The silhouette is a soft wavy
  bob with several broad, irregular clumps framing the cheeks.
- Keep plausible volume close to the skull, with local lift at the part and
  temples. Avoid a tall ponytail, a huge top mass, or large sculpted loops.
- A few fine flyaways and varied strand highlights should soften the outer
  edge. A simplified clump/curve solution is acceptable if the silhouette and
  anisotropic highlights read naturally at the delivery resolution.
- Start hair roughness around 0.25–0.40 and tune under the actual key light.
  The result should resemble hair rather than a smooth dark plastic helmet.
- Test a small head turn in the preview stage: the hairstyle must retain its
  volume and not expose scalp gaps or jump between frames.

## Skin and materials

- Warm peach/tan skin with gentle cheek, ear and nose color variation. Keep
  the face warmer than the cream wall and sage clothing around it.
- Subtle subsurface softness around cheeks, ears and nose; preserve the nose
  bridge, lips and eyelids. Avoid waxy translucency or an opaque chalk surface.
- For a meter-scale character, start with a shallow physical scattering
  distance around 1–3 mm, then tune by the result. A Principled skin setup
  with moderate subsurface weight and roughness around 0.4–0.55 is a useful
  starting point, not a fixed recipe.
- Skin detail should be lower amplitude than the expression. Do not place
  visible grain or heavy bump across the eyelids, nose and lips.
- Eyes need a moist corneal highlight and a shaped upper-lid shadow. Keep the
  highlight consistent with the large window/key light, rather than adding
  unrelated bright dots to make the eyes look alive.
- Clothing is matte knit/cotton; paint is softly rough; counters are pale
  wood; metal has broad, restrained highlights. Avoid a uniform plastic
  roughness on the character and the entire room.

## Wardrobe and prop scale

Use one outfit through the home, platform, and train sequence:

- Simple light sage crew-neck knit pullover, natural fabric thickness and
  folds, relaxed sleeves. The reference's plain knit garment is a better
  guide than Ellie's short buttoned jacket with breast pockets.
- Full-length medium/dark-blue jeans and ordinary understated trainers or
  flats. Do not use shorts, oversized combat boots, or child-like accessories.
- A modest cream canvas shoulder bag, approximately 28–32 cm wide, 23–27 cm
  high and 9–12 cm deep, sized to contain the bottle and wallet. The script
  says a small bag; do not turn it into an oversized rigid grocery box.
- Bottle approximately 22–25 cm tall, phone approximately 15 × 7 cm, wallet
  approximately 10 × 8 cm. Keep those dimensions fixed between shots.
- A soft bag opening needs visible depth. Bottle and phone must enter that
  opening, with the hand maintaining its grip until the prop is supported.

## Camera and composition

The reference hero image has an adult waist-up figure left of center, a bag
and reachable working surface to the right, and a soft kitchen behind her.

For the first hero preview at 16:9, use these image-space guides:

- Lily's face center near x=0.33–0.37 of frame width.
- Skull/hair crown near y=0.07–0.10; eye line around y=0.26–0.30.
- Crown-to-chin occupies approximately 0.32–0.38 of image height in this
  close/medium framing; do not achieve that by making the actual head huge.
- Show her shoulders, torso and part of the forearms; crop near the waist.
- Put the bag/action area near x=0.64–0.75, with an unobstructed hand path.
- Keep the background window and cabinets readable as a place, while their
  small details are softer than her eyes and lips.

Start with a 50–65 mm lens on a 36 mm sensor. Place the camera around upper
chest/eye height with only a modest downward angle. Adjust distance and aim
to meet the framing guides; avoid the broad close-camera perspective that
makes the forehead, eyes, hands or props swell toward the viewer.

Focus on the eyes. A starting f-stop around 2.8–4, with useful separation
between character and rear wall, should provide gentle depth separation.
The phone/packing insert can have a deeper focus range so the hand, bag rim
and key text are simultaneously readable. A shallow-focus effect must not
hide an incorrect grasp or remove the station/train context.

In station shots, retain adult proportions and the same lens family. A
medium-wide frame must show recognizable platform paving, shelter/columns,
railway signage, and a train with windows and an open doorway. A flat slab
behind Lily is insufficient to establish a station or train.

## Lighting and image finish

- Large, soft daylight key from camera-left/front-left, supported by the
  visible window and pale room bounce. Use a broad source, not a tiny hard
  spotlight or uniform ambient illumination.
- Preserve a modest light-to-shadow ratio on the face, approximately 2:1 to
  3:1 as a starting point. The far cheek should retain shape without becoming
  a dark dramatic portrait.
- Use warm neutral daylight, approximately 5000–5600 K, with warm wood/cream
  bounce. Avoid the previous washed-out grey-green face and white room.
- Keep a soft upper-lid shadow, cheek modeling, a small chin shadow, and
  gentle hair edge light. These cues make the face feel dimensional.
- Windows may be bright, but should retain frames and local shape. Cabinets
  should not merge into a featureless white field.
- Use a filmic/AgX transform with controlled highlights and moderate contrast.
  Match the resulting picture, not just a named look or exposure value.
- Evaluate the face at the final viewing size. Render grain, blotchy
  denoising, sparkling hair, or temporal ghosting across the eyes and mouth
  are failures for this language-learning presentation.

## Acting and animation

- Begin from a relaxed, mild smile. A greeting is a small open-hand gesture
  with natural elbow bend, not a large repeated arm swing.
- Gaze should move purposefully between camera, Anna's picture, clock,
  timetable, bottle, bag and train. Check the world-space target: previous
  frames sometimes looked away from the prop being discussed.
- Use occasional short blinks; eyelids must move over the eyeballs without
  the pupil or cornea clipping through them.
- Speech needs coordinated jaw and lip/cheek shapes. Audio amplitude can
  assist timing, but should not be described as exact phoneme lip sync.
- For prop actions, constrain the held prop to the hand or animate both to
  a tested shared contact path. Curved fingers, wrist alignment, and release
  timing must be visible. Do not substitute a floating prop or hide a known
  contact error with a different camera.
- Boarding requires an open stationary train door, a planted support foot,
  a real step into the vestibule, and the same bag retained in the same hand.
  The train must not start moving while Lily is still crossing the threshold.
- Render native animation frames for the approved motion. Do not use the
  previous 6-to-24 fps optical-flow interpolation as the final solution for
  hands, hair, eyes and lips; it introduced visible doubled/smeared edges.

## Concrete CPU look-development checks before production rendering

These are the next review artifacts, not a request to render the complete
video. No GPU/full-sequence render should precede an acceptable preview set.

1. **Character sheet:** neutral front, smiling front, three-quarter and
   full-body views under one soft studio light. Confirm adult proportions,
   relaxed lids, shaped lips/nose, shoulder-length hair and final outfit.
2. **Reference-matched hero frame:** new Lily and small bag in the home set,
   using the framing guides above. Compare side by side at the same display
   size. Check skin warmth, eye size, nose/cheek modeling, hair silhouette,
   cloth roughness, window exposure and background softness.
3. **Station/platform frame:** same Lily, outfit and bag beside a recognizable
   regional train and platform. Check adult scale against a real door height,
   readable Greenfield/departure signage and coherent daylight direction.
4. **Train doorway/interior frame:** verify that the door, step, floor, seat
   and window establish an actual passenger train. Keep the character scale
   and face treatment consistent with the home hero frame.
5. **Packing contact strip:** four CPU stills at reach, secure grip, bottle
   over opening, and supported/released inside bag. Every intermediate state
   should be physically believable; hands and props must remain in focus.
6. **Expression strip:** neutral, greeting smile, mild surprise, hopeful glance,
   and two speech vowel shapes. Reject worried default brows, circular staring
   whites, black gaping mouths, or eyes that lose a common target.

Use small low-sample CPU renders for camera blocking. For material/face
acceptance, create at least a clean 960×540 preview with enough CPU samples
and spatial denoising to judge eyes, skin and hair. A noisy 4-sample image
cannot validate the finished appearance. Judge animation separately with a
short native-frame CPU preview after the stills match, before rendering all
1320 timeline frames.

## Story logic and continuity

See `storyboard.json` for the 12-shot, 55-second sequence. The early town and
station images are illustrative destination/schedule cutaways, with Lily
still at home. The return to the 9:00 home clock therefore remains coherent.
After packing and Anna's message, a clear montage cut advances to the real
station visit. This gives home, town, station, platform and train visuals
without pretending the entire journey occurs in 55 seconds of real time.

One phone, one wallet, one bottle, one bag and one outfit persist throughout.
The wallet enters the bag first; the phone is put down to free the hand for
the bottle, and packed after Anna's message. Bag contents should not reset
between shots. Keep all 12 original spoken lines unchanged.
