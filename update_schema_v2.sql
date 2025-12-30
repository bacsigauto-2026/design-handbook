-- Rename drawing_name to drawing_title (matches user request)
ALTER TABLE design_docs RENAME COLUMN drawing_name TO drawing_title;

-- Add new columns
ALTER TABLE design_docs
ADD COLUMN IF NOT EXISTS project_number TEXT,
ADD COLUMN IF NOT EXISTS location TEXT,
ADD COLUMN IF NOT EXISTS client TEXT,
ADD COLUMN IF NOT EXISTS consultant TEXT,
ADD COLUMN IF NOT EXISTS designer TEXT,
ADD COLUMN IF NOT EXISTS year INTEGER,
ADD COLUMN IF NOT EXISTS berth_type TEXT,
ADD COLUMN IF NOT EXISTS design_stage TEXT,
ADD COLUMN IF NOT EXISTS vessel_type TEXT,
ADD COLUMN IF NOT EXISTS vessel_size INTEGER,
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS note TEXT,
ADD COLUMN IF NOT EXISTS pdf_folder TEXT,
ADD COLUMN IF NOT EXISTS pdf_files TEXT,
-- pdf_link exists
ADD COLUMN IF NOT EXISTS pdf_page INTEGER,
-- catalogue exists
ADD COLUMN IF NOT EXISTS sub_catalogue TEXT,
ADD COLUMN IF NOT EXISTS structural_type TEXT,
ADD COLUMN IF NOT EXISTS sub_structural_type TEXT,
-- drawing_title is renamed above
ADD COLUMN IF NOT EXISTS drawing_number TEXT,
ADD COLUMN IF NOT EXISTS drawing_rev TEXT,
ADD COLUMN IF NOT EXISTS drawing_date TEXT, -- User requested String
ADD COLUMN IF NOT EXISTS drawing_description TEXT,
ADD COLUMN IF NOT EXISTS drawing_information TEXT;
