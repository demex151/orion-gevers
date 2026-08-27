# GEVER Real Runtime Tools Design

## Goal
Make GEVER work end-to-end in real use: microphone capture must terminate reliably, and a spoken request to search for painting clients must execute Lead Hunter instead of only asking NVIDIA for a conversational answer.

## Runtime flow
1. Voice input is captured with finite defaults so silence closes the phrase instead of leaving the microphone open indefinitely.
2. `GeversBrain.think()` first checks whether the request is an explicit Lead Hunter command.
3. Lead Hunter commands execute the existing V2 pipeline and return a deterministic summary built from persisted results.
4. Normal conversation continues through the NVIDIA model exactly as before.
5. No lead is invented. If Lead Hunter returns zero accepted opportunities, GEVER states that clearly.

## Boundaries
- Keep Lead Hunter V2 filters unchanged.
- Do not add Nextdoor or other account integrations in this change.
- Do not automate outreach.
- Preserve NVIDIA as the normal conversational brain.
- Preserve current memory behavior for normal conversation.

## Voice behavior
`GeversListener.listen()` will use finite defaults when the caller does not supply limits. The API endpoint must also stop passing explicit `None` values that override safe defaults.

## Tool routing
A small deterministic intent router will recognize Spanish and English variants for finding painting leads, such as `busca clientes`, `busca oportunidades`, `buscar leads`, `find painting leads`, and explicit references to Gevers Painting. Matching requests execute Lead Hunter directly.

## Lead Hunter response
- Zero accepted: report that the search completed and no valid recent opportunities were found.
- One or more accepted: report count and summarize the top leads with evidence/source URLs for UI/API consumers; spoken output can remain concise.
- Provider failures may be mentioned without turning zero results into invented opportunities.

## Tests
Add unit tests for finite listener defaults and deterministic Lead Hunter routing. Existing Lead Hunter and voice tests must remain green.