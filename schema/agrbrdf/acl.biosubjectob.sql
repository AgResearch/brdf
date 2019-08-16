--
-- Name: biosubjectob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosubjectob FROM PUBLIC;
REVOKE ALL ON TABLE biosubjectob FROM agrbrdf;
GRANT ALL ON TABLE biosubjectob TO agrbrdf;
GRANT SELECT ON TABLE biosubjectob TO gbs;


