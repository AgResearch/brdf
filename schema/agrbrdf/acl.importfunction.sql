--
-- Name: importfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE importfunction FROM PUBLIC;
REVOKE ALL ON TABLE importfunction FROM agrbrdf;
GRANT ALL ON TABLE importfunction TO agrbrdf;
GRANT SELECT ON TABLE importfunction TO gbs;


