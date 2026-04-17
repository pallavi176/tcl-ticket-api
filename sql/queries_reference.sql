-- Logical SQL equivalents of the SQLAlchemy operations used by this service.
-- The application uses the ORM (no stored procedures); DB triggers are not required.

-- POST /tickets (create)
-- INSERT INTO tblTicketDetails
--   (title, description, status, priority, assigned_to)
-- VALUES (?, ?, ?, ?, ?);
-- MySQL sets ticket_id, created_at, updated_at automatically.

-- GET /tickets/:id (read)
-- SELECT ticket_id, title, description, status, priority, created_at, updated_at, assigned_to
-- FROM tblTicketDetails
-- WHERE ticket_id = ?;

-- GET /tickets (list, paginated — newest first)
-- SELECT ... FROM tblTicketDetails
-- ORDER BY created_at DESC
-- LIMIT ? OFFSET ?;

-- PATCH /tickets/:id (same partial update semantics as PUT)
-- PUT /tickets/:id (partial update — only provided columns)
-- UPDATE tblTicketDetails
-- SET title = COALESCE(?, title),
--     description = ?,
--     status = COALESCE(?, status),
--     priority = COALESCE(?, priority),
--     assigned_to = ?
-- WHERE ticket_id = ?;
-- updated_at is maintained by ON UPDATE CURRENT_TIMESTAMP on the column definition.

-- POST /tickets/:id/close (sets status to closed — same as PATCH with body {"status":"closed"})
-- UPDATE tblTicketDetails SET status = 'closed' WHERE ticket_id = ?;
