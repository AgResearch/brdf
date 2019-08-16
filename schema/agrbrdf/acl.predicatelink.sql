--
-- Name: predicatelink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE predicatelink FROM PUBLIC;
REVOKE ALL ON TABLE predicatelink FROM agrbrdf;
GRANT ALL ON TABLE predicatelink TO agrbrdf;
GRANT SELECT ON TABLE predicatelink TO gbs;


