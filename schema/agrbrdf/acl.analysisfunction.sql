--
-- Name: analysisfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE analysisfunction FROM PUBLIC;
REVOKE ALL ON TABLE analysisfunction FROM agrbrdf;
GRANT ALL ON TABLE analysisfunction TO agrbrdf;
GRANT SELECT ON TABLE analysisfunction TO gbs;


