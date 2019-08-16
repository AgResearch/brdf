--
-- Name: urilink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE urilink FROM PUBLIC;
REVOKE ALL ON TABLE urilink FROM agrbrdf;
GRANT ALL ON TABLE urilink TO agrbrdf;
GRANT SELECT ON TABLE urilink TO gbs;


