--
-- Name: importfunctionfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE importfunctionfact FROM PUBLIC;
REVOKE ALL ON TABLE importfunctionfact FROM agrbrdf;
GRANT ALL ON TABLE importfunctionfact TO agrbrdf;
GRANT SELECT ON TABLE importfunctionfact TO gbs;


