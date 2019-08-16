--
-- Name: ob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ob FROM PUBLIC;
REVOKE ALL ON TABLE ob FROM agrbrdf;
GRANT ALL ON TABLE ob TO agrbrdf;
GRANT SELECT ON TABLE ob TO gbs;


