# Staff Task Board Research Notes

## Reference: Notion Databases
- Multiple view types: table (default grid), board (column grouping), timeline/calendar, gallery, list.
- Persistent filters and sorts per view; quick toggle between saved presets.
- Property management: control visibility, rename headers, inline editing within each view.
- Quick creation buttons and templates; contextual actions (duplicate, assign, status update).
- Rich card previews in board view with badges, progress indicators, and metadata chips.
- Bulk operations: multi-select rows, batch status/assignee adjustments.

## Current OOBC Staff Task Board (as of Sept 2024)
- Single Kanban column layout grouped by status; cards expose priority, team, assignee, due date, progress.
- Filters for status, priority, team, assignee, keyword search; metrics highlight totals/completion.
- Inline update form per card to change status/progress; no drag-and-drop.
- No alternative layouts (table/list), grouping options, or saved configurations.
- Server-rendered; no API endpoints dedicated to tasks beyond view.

## Opportunity Areas
1. **View Modes**: Introduce `table` and `board` view toggles, with flexibility to add `timeline`/`calendar` later.
2. **Dynamic Grouping**: Allow board view grouping by status, priority, or team to mimic Notion board grouping.
3. **Sorting Controls**: Provide sort selectors for table view (e.g., due date, priority, assignee).
4. **Property Visibility**: Support toggling column visibility or at least display richer metadata badges.
5. **Inline Actions**: Add quick actions (mark complete, update progress, reassign) without full reload via minimal JS.
6. **Saved Filters/View Presets**: Lay groundwork for persisting chosen view/group/sort via query params.
7. **Design Enhancements**: Use clean card/table styling, badges, progress bars mirroring Notion aesthetics.

## Toward MVP Alignment
- Implement server-rendered multi-view interface with progressive enhancement using lightweight JavaScript.
- Maintain existing filtering while extending to support new parameters (`view`, `group`, `sort`, `order`).
- Ensure accessibility and responsiveness akin to Notion's grid/board layouts.
- Keep backend changes minimal: reuse `StaffTask` queryset with dynamic grouping pipeline builder.
- Provide hooks for future async upgrades (HTMX/fetch) by exposing JSON-ready context structures.
