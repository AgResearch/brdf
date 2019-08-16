--
-- Name: biosequenceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequenceob FROM PUBLIC;
REVOKE ALL ON TABLE biosequenceob FROM agrbrdf;
GRANT ALL ON TABLE biosequenceob TO agrbrdf;
GRANT SELECT ON TABLE biosequenceob TO gbs;


