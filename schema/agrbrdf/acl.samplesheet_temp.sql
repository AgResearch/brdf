--
-- Name: samplesheet_temp; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE samplesheet_temp FROM PUBLIC;
REVOKE ALL ON TABLE samplesheet_temp FROM agrbrdf;
GRANT ALL ON TABLE samplesheet_temp TO agrbrdf;
GRANT SELECT ON TABLE samplesheet_temp TO gbs;


