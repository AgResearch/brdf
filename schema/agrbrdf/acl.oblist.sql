--
-- Name: oblist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oblist FROM PUBLIC;
REVOKE ALL ON TABLE oblist FROM agrbrdf;
GRANT ALL ON TABLE oblist TO agrbrdf;
GRANT SELECT,INSERT,DELETE ON TABLE oblist TO gbs;


