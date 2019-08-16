--
-- Name: biodatabaseob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biodatabaseob FROM PUBLIC;
REVOKE ALL ON TABLE biodatabaseob FROM agrbrdf;
GRANT ALL ON TABLE biodatabaseob TO agrbrdf;
GRANT SELECT ON TABLE biodatabaseob TO gbs;


