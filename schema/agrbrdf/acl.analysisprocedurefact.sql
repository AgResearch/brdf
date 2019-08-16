--
-- Name: analysisprocedurefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE analysisprocedurefact FROM PUBLIC;
REVOKE ALL ON TABLE analysisprocedurefact FROM agrbrdf;
GRANT ALL ON TABLE analysisprocedurefact TO agrbrdf;
GRANT SELECT ON TABLE analysisprocedurefact TO gbs;


