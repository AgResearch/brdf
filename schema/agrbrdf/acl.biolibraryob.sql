--
-- Name: biolibraryob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biolibraryob FROM PUBLIC;
REVOKE ALL ON TABLE biolibraryob FROM agrbrdf;
GRANT ALL ON TABLE biolibraryob TO agrbrdf;
GRANT SELECT ON TABLE biolibraryob TO gbs;


